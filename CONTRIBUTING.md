# Contributing to LangGraph Scrum Team

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/AIDevelopment.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit with a descriptive message
7. Push and create a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install dashboard dependencies
cd dashboard && npm install
```

## Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Use strict mode, prefer interfaces over types
- **Commits**: Use conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)

## Pull Request Guidelines

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

## Reporting Issues

When reporting issues, please include:
- Python/Node.js version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

## Questions?

Open a discussion on GitHub or reach out to the maintainers.
