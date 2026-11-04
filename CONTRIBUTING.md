# Contributing to NexaCart AI Customer Support Desk

Thank you for your interest in NexaCart AI Customer Support Desk!

## Getting Started

1. Fork the repository.
2. Clone your fork to your local machine.
3. Create a Python virtual environment.
4. Install dependencies from `requirements.txt`.
5. Create your `.env` file using `.env.example`.
6. Run the application and tests locally.

## Development Guidelines

- Follow existing Python coding conventions.
- Keep agent responsibilities modular and focused.
- Ensure responses remain grounded in retrieved knowledge.
- Preserve QA validation and deterministic escalation guardrails.
- Add or update tests when modifying functionality.
- Do not commit API keys, credentials, or sensitive customer data.

## Testing

Run the test suite:

```bash
pytest -v
```

Ensure all tests pass before submitting changes.

## Pull Requests

1. Describe the purpose and scope of your changes.
2. Include relevant test results.
3. Reference related issues, if applicable.
4. Ensure GitHub Actions checks pass.

## Reporting Issues

Please provide a clear description, steps to reproduce, expected behavior, and actual behavior when reporting bugs.

Thank you.