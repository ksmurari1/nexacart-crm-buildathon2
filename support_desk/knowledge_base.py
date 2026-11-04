"""NexaCart document ingestion and hybrid retrieval (BM25 + dense vectors + RRF).

Supports Markdown, TXT and PDF. If a PDF and its Markdown twin share a filename stem,
PDF is preferred to avoid indexing duplicate content. FAISS indexes and dense vectors
are cached locally in vector_store/ and rebuilt when the corpus changes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


from .config import KB_DIR, ROOT, get_settings


STOPWORDS = set("""a an the and or but if of to in on at for with from by is are was were be been it its this that
 i me my we our you your they them their he she his her can could would should will do does did have has had
 not no so as up out about how what when where which who why get got just still please hi hello thanks thank
 there here than then into over also any all some am""".split())

@dataclass(frozen=True)
class Passage:
    id: str
    source: str
    section: str
    text: str
    page: int | None = None
    department: str = "Customer Support"
    policy_year: int | None = None

    def to_dict(self, score: float | None = None) -> dict:
        d = {"id": self.id, "source": self.source, "section": self.section, "text": self.text,
             "department": self.department}
        if self.page is not None:
            d["page"] = self.page
        if self.policy_year is not None:
            d["policy_year"] = self.policy_year
        if score is not None:
            d["score"] = round(float(score), 4)
        return d


def tokenize(text: str) -> list[str]:
    # Includes Latin letters, numbers, and Tamil Unicode blocks.
    tokens = re.findall(r"[a-z0-9]+|[\u0B80-\u0BFF]+", (text or "").lower())
    return [_stem(t) for t in tokens if t not in STOPWORDS and len(t) > 1]


def _stem(token: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[:-len(suffix)]
    return token


def _metadata(path: Path, text: str) -> tuple[str, int | None]:
    name = path.stem.lower()
    department = ("Payments & Finance" if "billing" in name or "payment" in name else
                 "Account Services" if "account" in name or "login" in name else
                 "Shipping & Logistics" if "shipping" in name or "delivery" in name else
                 "Returns & Product Support" if "refund" in name or "product" in name else
                 "Customer Support")
    year_match = re.search(r"\b(20\d{2})\b", text)
    return department, int(year_match.group(1)) if year_match else None


def _chunk_text(text: str, max_chars: int = 1100, overlap: int = 140) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", (text or "").strip())
    if len(text) <= max_chars:
        return [text] if text else []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = max(text.rfind("\n\n", start, end), text.rfind(". ", start, end))
            if boundary > start + max_chars * 0.55:
                end = boundary + (2 if text[boundary:boundary+2] == ". " else 0)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def _split_md(path: Path) -> list[Passage]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    # Split on Markdown headings while preserving the heading in the section label.
    parts = re.split(r"(?m)^#{1,3}\s+", raw)
    headings = re.findall(r"(?m)^#{1,3}\s+(.+)$", raw)
    if not headings:
        parts, headings = [raw], ["Overview"]
    else:
        # re.split creates a preamble before first heading; discard only if empty.
        if parts and not parts[0].strip():
            parts = parts[1:]
        headings = headings[:len(parts)]
    department, year = _metadata(path, raw)
    out = []
    idx = 0
    for section, body in zip(headings, parts):
        for chunk in _chunk_text(body):
            idx += 1
            out.append(Passage(f"{path.name}#{idx}", path.name, section.strip(), chunk,
                              department=department, policy_year=year))
    return out


def _split_pdf(path: Path) -> list[Passage]:
    """Extract page-aware passages and recognize short policy section headings."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        out: list[Passage] = []
        department, year = _metadata(path, " ".join((p.extract_text() or "") for p in reader.pages))
        idx = 0
        for page_no, page in enumerate(reader.pages, 1):
            raw = (page.extract_text() or "").strip()
            if not raw:
                continue
            lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines() if line.strip()]
            # Strip repeated PDF running header/footer and metadata lines.
            lines = [line for line in lines if not line.startswith("NexaCart · Internal")
                     and not line.startswith("NEXACART · CUSTOMER")
                     and not re.match(r"^Page\s+\d+$", line)
                     and not line.startswith("Document owner:")
                     and line not in {path.stem.replace("_", " ").title(), "NexaCart Support Desk"}]
            section = "Overview"
            buffer: list[str] = []
            def flush() -> None:
                nonlocal idx, buffer
                body = "\n".join(buffer).strip()
                if len(body) >= 25:
                    idx += 1
                    out.append(Passage(f"{path.name}#p{page_no}-s{idx}", path.name, section, body,
                                      page_no, department, year))
                buffer = []
            for line in lines:
                is_heading = (len(line) <= 72 and not line.endswith((".", ":", ";"))
                             and not re.match(r"^(\d+[.)]|[-•])\s", line)
                             and len(line.split()) <= 8
                             and not line.lower().startswith(("http", "www")))
                # The first page title is not a policy section; skip it as a heading.
                if is_heading and line.lower() not in {"refund policy", "shipping & delivery policy",
                        "product faq", "account & login help", "payments & billing policy"}:
                    flush()
                    section = line
                else:
                    buffer.append(line)
            flush()
        return out
    except Exception as exc:
        return [Passage(f"{path.name}#error", path.name, "Extraction error",
                       f"PDF could not be parsed: {type(exc).__name__}: {exc}")]


class KnowledgeBase:
    def __init__(self, kb_dir: Path = KB_DIR, vector_dir: Path | None = None):
        self.kb_dir = Path(kb_dir)
        self.vector_dir = Path(vector_dir or (ROOT / "vector_store"))
        self.passages: list[Passage] = []
        files = sorted(self.kb_dir.glob("*"))
        pdf_stems = {f.stem.lower() for f in files if f.suffix.lower() == ".pdf"}
        for f in files:
            suffix = f.suffix.lower()
            if suffix == ".md" and f.stem.lower() in pdf_stems:
                continue  # prefer PDF twin to prevent duplicate retrieval
            if suffix == ".md":
                self.passages.extend(_split_md(f))
            elif suffix == ".txt":
                text = f.read_text(encoding="utf-8", errors="ignore")
                department, year = _metadata(f, text)
                self.passages.append(Passage(f"{f.name}#1", f.name, "Document", text,
                                          department=department, policy_year=year))
            elif suffix == ".pdf":
                self.passages.extend(_split_pdf(f))

        self._docs = [Counter(tokenize(f"{p.section} {p.section} {p.text}")) for p in self.passages]
        self._avg_len = sum(sum(d.values()) for d in self._docs) / max(len(self._docs), 1)
        df = Counter(term for d in self._docs for term in d)
        n = len(self._docs)
        self._idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self._dense = None
        self._vectorizer = None
        self._faiss = None
        self.dense_backend = "not initialized"
        self.corpus_hash = self._corpus_hash()
        self._build_dense()

    def _corpus_hash(self) -> str:
        h = hashlib.sha256()
        for p in self.passages:
            h.update(f"{p.id}\0{p.text}\0".encode("utf-8"))
        return h.hexdigest()

    def _build_dense(self) -> None:
        if not self.passages:
            self.dense_backend = "empty knowledge base"
            return
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        texts = [p.text for p in self.passages]
        settings = get_settings()
        model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        cache_key = hashlib.sha256(f"{self.corpus_hash}:{model_name}:{bool(settings.api_key)}".encode()).hexdigest()[:20]
        vector_file = self.vector_dir / f"vectors-{cache_key}.npy"
        meta_file = self.vector_dir / f"vectors-{cache_key}.json"

        # Load a valid embedding cache first; prevents repeated API calls at every app restart.
        if settings.api_key and vector_file.exists() and meta_file.exists():
            try:
                import numpy as np
                meta = __import__("json").loads(meta_file.read_text(encoding="utf-8"))
                if meta.get("corpus_hash") == self.corpus_hash and meta.get("model") == model_name:
                    self._set_dense(np.load(vector_file).astype("float32"), backend="OpenAI embeddings (cached)")
                    if self._dense is not None:
                        return
            except Exception:
                pass

        if settings.api_key:
            try:
                from openai import OpenAI
                import numpy as np
                client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
                vectors = []
                for start in range(0, len(texts), 64):
                    response = client.embeddings.create(model=model_name, input=texts[start:start+64])
                    vectors.extend(item.embedding for item in response.data)
                arr = np.asarray(vectors, dtype="float32")
                np.save(vector_file, arr)
                meta_file.write_text(json.dumps({"corpus_hash": self.corpus_hash, "model": model_name}), encoding="utf-8")
                self._set_dense(arr, backend="OpenAI embeddings")
                if self._dense is not None:
                    return
            except Exception:
                self.dense_backend = "OpenAI embeddings unavailable; using offline vectors"

        try:
            import numpy as np
            from sklearn.feature_extraction.text import HashingVectorizer
            self._vectorizer = HashingVectorizer(n_features=4096, alternate_sign=False, norm="l2",
                                                ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
            self._dense = self._vectorizer.transform(texts).astype("float32")
            self.dense_backend = "offline hashing vectors"
            try:
                import faiss
                dense = self._dense.toarray()
                index_path = self.vector_dir / f"faiss-{self.corpus_hash[:20]}.index"
                if index_path.exists():
                    self._faiss = faiss.read_index(str(index_path))
                    if self._faiss.ntotal != len(self.passages):
                        self._faiss = None
                if self._faiss is None:
                    self._faiss = faiss.IndexFlatIP(dense.shape[1])
                    self._faiss.add(dense)
                    faiss.write_index(self._faiss, str(index_path))
                self.dense_backend = "FAISS + offline hashing vectors (cached)"
            except Exception:
                self._faiss = None
        except Exception:
            self._dense = None
            self.dense_backend = "dense retrieval unavailable"

    def _set_dense(self, arr, backend: str = "OpenAI embeddings") -> None:
        import numpy as np
        arr = np.asarray(arr, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = arr / (norms + 1e-12)
        try:
            import faiss
            index_path = self.vector_dir / f"faiss-openai-{self.corpus_hash[:20]}.index"
            self._faiss = None
            if index_path.exists():
                try:
                    cached = faiss.read_index(str(index_path))
                    if cached.ntotal == arr.shape[0] and cached.d == arr.shape[1]:
                        self._faiss = cached
                except Exception:
                    self._faiss = None
            if self._faiss is None:
                self._faiss = faiss.IndexFlatIP(arr.shape[1])
                self._faiss.add(arr)
                faiss.write_index(self._faiss, str(index_path))
            self._dense = arr
            self.dense_backend = f"FAISS + {backend} (persistent index)"
        except Exception:
            self._dense = arr
            self.dense_backend = f"NumPy + {backend}"

    def documents(self) -> list[dict]:
        docs = []
        pdf_stems = {f.stem.lower() for f in self.kb_dir.glob("*.pdf")}
        for f in sorted(self.kb_dir.glob("*")):
            if f.suffix.lower() in {".md", ".txt"}:
                if f.suffix.lower() == ".md" and f.stem.lower() in pdf_stems:
                    continue
                docs.append({"name": f.name, "title": f.stem.replace("_", " ").title(),
                            "content": f.read_text(encoding="utf-8", errors="ignore")})
            elif f.suffix.lower() == ".pdf":
                docs.append({"name": f.name, "title": f.stem.replace("_", " ").title(),
                            "content": f"[PDF document · {f.stat().st_size:,} bytes]"})
        return docs

    def get(self, pid: str) -> Passage | None:
        return next((p for p in self.passages if p.id == pid), None)

    def _bm25(self, query: str, top_k: int = 8, k1: float = 1.4, b: float = 0.75):
        terms = tokenize(query)
        if not terms:
            return []
        scored = []
        for p, doc in zip(self.passages, self._docs):
            length = sum(doc.values())
            score = sum(self._idf.get(t, 0) * doc[t] * (k1 + 1) /
                        (doc[t] + k1 * (1 - b + b * length / max(self._avg_len, 1e-9)))
                        for t in set(terms) if t in doc)
            if score > 0:
                scored.append((p, score))
        return sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]

    def _dense_search(self, query: str, top_k: int = 8):
        if self._dense is None:
            return []
        import numpy as np
        if self._vectorizer is not None:
            q = self._vectorizer.transform([query]).astype("float32")
            if self._faiss is not None:
                scores, ids = self._faiss.search(q.toarray(), min(top_k, len(self.passages)))
                return [(self.passages[int(i)], float(s)) for s, i in zip(scores[0], ids[0]) if i >= 0]
            qv = q.toarray()[0]
            scores = np.asarray(self._dense.dot(qv)).reshape(-1)
        else:
            try:
                from openai import OpenAI
                settings = get_settings()
                client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
                model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
                qv = np.asarray(client.embeddings.create(model=model, input=[query]).data[0].embedding, dtype="float32")
                qv = qv / (np.linalg.norm(qv) + 1e-12)
                scores = self._dense @ qv
            except Exception:
                return []
        idx = np.argsort(scores)[::-1][:top_k]
        return [(self.passages[int(i)], float(scores[i])) for i in idx]

    
    
    def search(self, query: str, top_k: int = 4, department: str | None = None,
                policy_year: int | None = None, **kwargs):
        """Hybrid retrieval with adaptive RRF ranking and metadata filtering."""
        if not tokenize(query):
            return []

        bm = self._bm25(query, max(top_k * 4, 12))
        dense = self._dense_search(query, max(top_k * 4, 12))

        offline_mode = self._vectorizer is not None
        dense_cutoff = 0.12 if offline_mode else 0.22
        dense = [(p, score) for p, score in dense if score >= dense_cutoff]

        # Adaptive RRF: trust lexical ranking more in offline hashing mode.
        bm_weight = 2.0 if offline_mode else 1.0
        dense_weight = 1.0

        # Offline-only intent boosts for policy-specific queries.
        source_intent = {}

        if offline_mode:
            q = query.lower()

            if any(term in q for term in [
                "delete account", "deactivate account",
                "close account", "account permanently"
            ]):
                source_intent["account_and_login.pdf"] = 0.025

            if any(term in q for term in [
                "shipping timeline", "delivery timeline",
                "standard shipping", "express shipping",
                "shipping fee", "delivery fee"
            ]):
                source_intent["shipping_policy.pdf"] = 0.025

            if any(term in q for term in [
                "warranty", "stopped working",
                "not working after", "coffee maker"
            ]):
                source_intent["product_faq.pdf"] = 0.025

        ranks = {}

        for rank, (p, _) in enumerate(bm, 1):
            ranks[p.id] = ranks.get(p.id, 0.0) + bm_weight / (60 + rank)

        for rank, (p, _) in enumerate(dense, 1):
            ranks[p.id] = ranks.get(p.id, 0.0) + dense_weight / (60 + rank)

        byid = {p.id: p for p in self.passages}

        # Apply small source-specific boosts only in offline fallback mode.
        if source_intent:
            for pid in ranks:
                passage = byid[pid]
                bonus = source_intent.get(Path(passage.source).name, 0.0)
                ranks[pid] += bonus

        ordered = sorted(ranks, key=ranks.get, reverse=True)

        results = []

        for pid in ordered:
            p = byid[pid]

            if department and department != "All" and p.department != department:
                continue

            if policy_year and p.policy_year != policy_year:
                continue

            results.append((p, ranks[pid]))

            if len(results) >= top_k:
                break

        return results



    @property
    def retrieval_info(self):
        return {"documents": len(self.documents()), "passages": len(self.passages),
                "dense_backend": self.dense_backend, "faiss_available": self._faiss is not None,
                "corpus_hash": self.corpus_hash}


@lru_cache(maxsize=1)
def get_kb():
    return KnowledgeBase()


def search_knowledge_base(query: str) -> str:
    hits = get_kb().search(query)
    if not hits:
        return "NO_MATCH: no policy or FAQ passage matches this query."
    return "\n\n".join(f"[{p.id}] ({p.source} > {p.section}) score={s:.4f}\n{p.text}" for p, s in hits)
