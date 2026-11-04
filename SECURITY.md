# Security Policy

## Supported Versions

The latest version of NexaCart AI Customer Support Desk on the `main` branch is currently supported with security updates.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

- Do not disclose sensitive information publicly.
- Contact the repository owner through GitHub for reporting security concerns.
- Include steps to reproduce the issue, if possible.

## Security Practices

This project follows these practices:

- API keys and credentials are stored in environment variables.
- `.env` files are excluded from version control.
- `.env.example` contains configuration placeholders only.
- Customer support responses are validated through QA and deterministic guardrails.
- Sensitive or uncertain customer cases are escalated for human review.

## Disclaimer

This is an educational and demonstration project. It is not intended for production deployment without additional security review, monitoring, and hardening.