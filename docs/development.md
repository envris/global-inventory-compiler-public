# Development guide
The following provides information about how the GIC is developed.

## Scope
### Adding fields
The GIC may be extended to support additional data types by adding files to the *fields* module. These fields are automatically detected and registered and require no further configuration of the existing code.

#### Identifier fields
Are string-based and can be used to compile and query a global inventory via the *Inventory* class. Dedicated identifier fields enable specialised validation and search behaviour compared to the more flexible *chemical_name* or *generic generic_id_\** fields. The *ec_number.py* and *inchikey.py* files are good reference implementations.

#### Data fields
Are any non-identifier field, which may be of any type. These are ignored by the Inventory class, but usable for analysis within the DataFrame. See the *rdk_mol.py* and *ghs_code.py* files provide good reference implementations.

### Unit tests
Each field has a corresponding unit test added to the *tests* directory.

### Out of scope
The GIC is a compiler and screening tool and accepts only one-dimensional values. Data requiring two or more dimensions (e.g., environmental measurements involving a value, sample matrix, and longitude–latitude components) cannot be processed.

### Application Programming Interface (API)
The workflow command-line scripts and the following top-level classes form the supported public API of the GIC:

* AssociatedValues
* DataFrame
* Inventory
* GenericExtractor
* GenericCsvExtractor
* GenericPdfExtractor
* GenericXlsxExtractor

Their public behaviour and method signatures should remain stable across versions.

## Methods
### Integrated Development Environment (IDE)
VSCode has been used to develop the GIC. Configuration settings, including format and extension settings, are maintained in the .vscode directory.

### Project setup
Runtime, optional, and development dependencies are declared in *pyproject.toml* and locked in *uv.lock*. Both files are committed. Set up a working tree with [uv](https://docs.astral.sh/uv/):

```shell
uv sync --locked --all-extras --all-groups
```

`--locked` fails if *uv.lock* is out of date with *pyproject.toml*, which catches accidental drift. `--all-extras` includes optional dependencies (if specified). `--all-groups` includes the *dev* dependency group (test, lint, and audit tooling).

The default Python version is pinned in *.python-version* (currently 3.12). To work against a different supported version locally, override with `uv python pin <version>` or set `UV_PYTHON=<version>` for one-off commands.

### Unit tests
Are executed using pytest, configured under `[tool.pytest.ini_options]` in *pyproject.toml*:

```shell
uv run pytest
```

The test coverage may be visualised using the Coverage Gutters extension for VSCode. A minimum level of coverage is not currently enforced.

### Code linting
Basic formatting and security checks are enforced by Ruff, which is configured in *ruff.toml*:

```shell
uv run ruff check
uv run ruff format --check
```

### Updating dependencies
To upgrade or add a dependency, edit *pyproject.toml* and regenerate the lockfile:

```shell
uv lock
```

To upgrade all dependencies to the latest compatible versions:

```shell
uv lock --upgrade
```

### Vulnerability and license auditing
Scan locked runtime dependencies for known vulnerabilities and disallowed licenses (only MIT and BSD-3-Clause are currently permitted):

```shell
bash scripts/audit-deps.sh
uv run python scripts/render-audit.py --output audit-summary.md
cat audit-summary.md
```

`audit-deps.sh` writes machine-readable findings to *audit.json* and *licenses.json*. `render-audit.py` converts them into a Markdown summary and sets the `has_findings` GitHub Actions output for use in CI gating.

The CI pipeline runs the same scripts on every pull request (advisory) and every release tag (gating). A scheduled run (Mondays 06:00 UTC) re-audits the locked dependencies against the latest vulnerability database and maintains a tracking issue labelled *dep-audit*. When using a development fork, issues must be manually enabled in *Settings* and the *dep-audit* label must also be created.

Addressing reported vulnerabilities typically requires upgrading the affected package and regenerating *uv.lock*.

## CI/CD
The above testing, linting, and auditing run automatically on push and pull requests targeting the *main* branch. See *.github/workflows/ci.yml*.
