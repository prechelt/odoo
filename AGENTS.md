# AGENTS.md

This file provides guidance to AI coding agents (including Claude Code) when working with code in this repository.

## What this is

Odoo — a monorepo ERP framework + ~626 business apps ("addons"), branch `19.0`. Roughly 883k lines
of Python and 1.1M lines of JavaScript. Two addons trees exist:

- `odoo/addons/` — core/framework modules only (`base`, plus `test_*` modules used by the framework's
  own test suite). ~24 modules.
- `addons/` — the actual business apps (`sale`, `crm`, `account`, `web`, `mail`, `website`, ...). ~626 modules.

The `odoo/` package itself (outside `odoo/addons/`) is the framework: ORM, HTTP layer, module loader,
CLI, test runner, etc.

## Local dev environment (this checkout)

A Postgres instance and config live under `myfork/` (not part of upstream Odoo):

```
myfork/docker-compose.yml   # postgres:17 container, user/pass "odoo", exposed on 127.0.0.1:5432
myfork/odoo.conf            # addons_path=/ws/ghf/odoo/addons,/ws/ghf/odoo/odoo/addons; data_dir under myfork/data
```

Start the DB:
`docker compose -f myfork/docker-compose.yml up -d`

## Commands

**Run the server:**
```
./odoo-bin -c myfork/odoo.conf
```

**Run tests** (Python). Tests are unittest-based; test classes are tagged (`@tagged`) with `standard`
and `at_install` by default. `--test-enable`/`--test-tags` implies `--stop-after-init`.
```
./odoo-bin -c myfork/odoo.conf -i <module> --test-enable --stop-after-init
./odoo-bin -c myfork/odoo.conf -u <module> --test-tags /module_name
./odoo-bin -c myfork/odoo.conf -u <module> --test-tags :TestClassName.test_method_name
```
`--test-tags` spec format: `[-][tag][/module][:class][.method][[params]]` — comma-separated, `-` to
exclude, `*` to match all tags. `-i` installs a module first, `-u` updates an already-installed one
(much faster for iterating on an existing module).

Test base classes live in `odoo/tests/common.py`: `TransactionCase` (rolls back per test method),
`SingleTransactionCase` (one transaction for the whole class), `HttpCase` (adds an HTTP test client
and browser-based "tour" support).

**Run JS unit tests:** modules that ship `static/tests/**/*.test.js` register them under the
`web.assets_unit_tests` bundle in their manifest; these run through the in-browser Hoot runner
(`addons/web/static/lib/hoot*`), not Node. Browser "tour" tests (`static/tests/tours/`) run under
`web.assets_tests` and are driven by `--test-tags` against the running server (e.g. a `HttpCase` that
starts a tour).

**Lint Python:** `ruff check` (config: `ruff.toml`, target `py310` minimum). Notable ignores include
line length, mutable class defaults, and several TRY/SIM rules — check `ruff.toml` before assuming a
rule applies. Import order: future / stdlib / third-party / `odoo` (first-party) / `odoo.addons`
(local-folder).

**Lint/format JS:** ESLint + Prettier, configured in `addons/web/tooling/_eslintrc.json` /
`_package.json` (there is no root `package.json`). Prettier: 4-space indent, double quotes, semicolons,
100-col width. Useful scripts from that package.json (run with `--config addons/web/tooling/_eslintrc.json`
or similar, since it's not at the repo root): `lint-all`, `lint-web`, `format-all`, `lint-diff`/`format-diff`
(diff-scoped variants for reviewing just changed lines).

## Architecture

### Framework (`odoo/`)

- `odoo/orm/` — the ORM: `models.py`/`model_classes.py` (recordsets, model metaclass), `fields*.py`
  (one file per field-type family: numeric, textual, temporal, relational, binary, selection,
  properties, reference), `domains.py` (search domain evaluation), `environments.py` (the `Environment`/
  cursor/user context threaded through every ORM call), `registry.py` (per-database model registry).
- `odoo/modules/` — module discovery, dependency graph resolution (`module_graph.py`), and the
  install/update loading sequence (`loading.py`).
- `odoo/tests/` — the test framework described above, plus `loader.py`/`suite.py` for test discovery
  and `tag_selector.py` for `--test-tags` parsing.
- `odoo/service/`, `odoo/http.py`, `odoo/orm/registry.py`'s multi-DB handling, `odoo/cli/` (subcommands
  for `odoo-bin`: `server`, `shell`, `scaffold`, `populate`, `i18n`, `db`, `deploy`, ...).
- `odoo/tools/config.py` — all CLI/config-file option definitions (this is the source of truth for
  every `odoo-bin` flag, e.g. `--test-tags`).

### Addon module layout (`addons/<name>/`)

Every module is declared by `__manifest__.py` — a dict literal with `depends` (other modules this one
requires; install order and data-loading order follow this graph), `data`/`demo` (XML/CSV files loaded
declaratively at install, in listed order), and `assets` (which JS/SCSS bundles the module's
`static/src/**` files belong to, e.g. `web.assets_backend`, `web.assets_frontend`,
`web.assets_tests`, `web.assets_unit_tests`).

Conventional subdirectories: `models/` (Python business objects), `views/` (XML view/action/menu
definitions), `security/` (`ir.model.access.csv` for model-level ACLs + XML record rules),
`controllers/` (HTTP routes), `wizard/` (transient models backing multi-step actions), `report/`
(QWeb/PDF reports), `data/`/`demo/` (XML/CSV data files referenced from the manifest), `static/src/`
(OWL components, SCSS), `static/tests/` (Hoot `*.test.js` unit tests, `tours/` for browser tours),
`tests/` (Python test cases, `common.py` per module for shared test setup/mixins).

A change to a model in module A can be overridden/extended by any module that depends on A (Odoo's
inheritance via `_inherit`); when tracing behavior, check for `_inherit = "model.name"` in downstream
modules, not just the model's defining module.

### Frontend

The web client (`addons/web`) is built on OWL 2 (`@odoo/owl`), Odoo's own component framework (not
React/Vue). Legacy jQuery-based UI still exists in older/less-maintained modules. Assets are bundled
per the `assets` key in manifests rather than via a root-level bundler config — there is no top-level
`package.json`/`webpack.config.js` to look for.
