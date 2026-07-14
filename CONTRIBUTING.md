# Contributing to okey-solver-py

Thank you for your interest in contributing to `okey-solver-py`! We welcome community contributions to help improve the solver performance, add rules support, and optimize our computer vision engines.

To ensure your contributions can be merged cleanly, please follow the guidelines below.

---

## 🛠 Local Development Setup

We use **Poetry** to manage dependencies, environments, and packaging.

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- [Poetry installed](https://python-poetry.org/docs/#installation) on your system

### 2. Clone and Initialize Virtualenv
```bash
# Clone the repository
git clone https://github.com/your-username/okey-solver-py.git
cd okey-solver-py

# Install dependencies including vision and server extras
poetry install --all-extras
```

---

## 🔒 Code Quality & Pre-commit Hooks

We enforce formatting and type checking on every commit to maintain code quality.

### 1. Install Pre-commit Hooks
Run this in the repository root to automatically run style checks before every commit:
```bash
poetry run pre-commit install
```

### 2. Manual Verification Commands

You can run these code-quality checks manually at any time:

- **Formatting & Linting (Ruff)**:
  ```bash
  poetry run ruff check src tests
  poetry run ruff format src tests
  ```
- **Type Checking (Mypy)**:
  ```bash
  poetry run mypy src
  ```

---

## 🧪 Running Tests

Our CI pipeline executes matrix builds across multiple Python versions and checks code coverage thresholds.

### Run Tests and Coverage Locally
```bash
# Run pytest with code coverage output
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

All contributions must maintain a minimum test coverage of **70%** and have clean static analysis checks to pass CI builds.

---

## 🚀 Creating Pull Requests

1. **Create a branch** for your feature or bug fix: `git checkout -b feature/my-cool-feature`.
2. **Commit changes** (make sure pre-commit hooks pass). We use structured commits to automatically generate release notes.
3. **Push to your fork** and open a Pull Request against the `main` branch.
