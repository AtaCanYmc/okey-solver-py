# okey-solver-py Documentation

Welcome to the documentation for **okey-solver-py**, an enterprise-grade Okey and Rummikub board arranger, solver, and computer vision integration library.

---

## Quick Navigation

- **[Architecture & Design Flow](ARCHITECTURE.md)**: Details on modular pipeline stages, decoupled packages (`okey_core`, `okey_solver`, `okey_vision`, `okey_orchestrator`), frame adapters, and async event observers.
- **[Game Rules & Heuristics](ALGORITHM_RULES.md)**: Explains rules governing run and group validation, Circular series handling (12-13-1), and Joker/False Okey resolutions.
- **[CLI Usage Reference](CLI_USAGE.md)**: Learn how to execute standard solvers and image predictions directly from the command line.

---

## FastAPI Microservice

Start the microservice server immediately:
```bash
pip install okey-solver-py[server]
okey-serve --port 8000
```
Then navigate to `/docs` for full interactive OpenAPI documentation.
