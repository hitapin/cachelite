# Contributing

Thanks for considering a contribution to CacheLite!

## Before you start

- Search existing issues and pull requests to avoid duplicate work.
- For a substantial change, open an issue first to discuss the problem and proposed approach.
- Keep changes focused and include tests for bug fixes and new behavior.

## Development setup

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
```

## Pull requests

Please include:

- A clear explanation of the problem and solution.
- Tests or a rationale for why tests are not applicable.
- Documentation updates when public behavior changes.
- Confirmation that the test suite passes locally.

By submitting a contribution, you agree that it may be distributed under the project's MIT license.
