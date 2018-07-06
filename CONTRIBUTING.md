# Contributing to extend-me

Thank you for your interest in contributing to extend-me!

## Contributing to this project

1. Fork the repository on [GitHub](https://github.com/katyukha/extend-me) or [GitLab](https://gitlab.com/katyukha/extend-me.git)
2. Create a new branch, e.g., `git checkout -b bug-12345` based on `dev` branch
3. Fix the bug or add the feature
4. Add or modify related help message (if necessary)
5. Add or modify documentation (if necessary) for your change
6. Add changelog entry for your change in *Unreleased* section
7. Commit and push it to your fork
8. Create Merge Request or Pull Request

## How to build documentation

Install [Sphinx](https://www.mkdocs.org/)

```bash
pip install sphinx
```

Build docs

```bash
(cd docs && make html)
```

Generated documents will be placed in `docs/build/html`
