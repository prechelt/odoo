# Facts for introducing country 'libyz'

This file is meant as a deposit for the knowledge we acquire over several
research sessions.
The knowledge will eventually be used to formulate an implementation plan.

Deposit here each piece of knowledge you find out that appears likely relevant for the goal.
Each "piece" (find a suitable granularity) or topic area should get its own section
with a level-3 heading.


## Goal

Libya has split. There is now still the old Libya and a new country called Libyz.
It has country code lz, so far the same phone prefix as Libya, and uses EUR as its currency.

Our goal is introducing this country and implementing its VAT system,
which requires that the tax rate is lower on Tuesdays than the rest of the week.
I will explain details upon request. Ask me for them when the time comes, but not before.


## What we know already


### Where country-specific (localization) logic lives

Country-specific accounting/fiscal logic lives in `addons/l10n_<code>/` modules, one per
country, named by ISO 3166-1 alpha-2 code (e.g. `l10n_de`, `l10n_fr`, `l10n_br`; 221 exist
in this checkout). A few modules cover multi-country regions instead of a single country
(`l10n_eu_oss`, `l10n_gcc_invoice`, `l10n_din5008` for DACH invoice layouts). There is no
separate index file listing them — the `addons/l10n_*` directory listing *is* the list.
For Libyz (code `lz`) this means we'd expect to add a new `addons/l10n_lz/` module.


### Where the master list of countries lives

The master list of countries/subdivisions (used for addresses, partners, etc., independent
of any localization logic) is the `res.country` model, seeded from
`odoo/addons/base/data/res_country_data.xml`, with subdivisions (states/provinces) in
`odoo/addons/base/data/res.country.state.csv`. This is where a brand-new country like Libyz
would need a `res.country` record added (with its own code `lz`, currency EUR, phone
prefix, etc.) before any localization module can reference it.


### How a country gets linked to its Chart of Accounts / fiscal templates

The link between a country and its available CoA/fiscal localization modules is built
dynamically at runtime, not via a static mapping file:
- Each `l10n_*` module registers its chart-of-accounts templates (tagged with a
  `country_id`) via the `@template` decorator in `addons/account/models/chart_template.py`.
- `ir.module.module.account_templates` (computed field, `addons/account/models/ir_module.py`)
  aggregates these registrations across all installed modules.
- `AccountChartTemplate._get_chart_template_mapping()` in `chart_template.py` builds the
  country → available-templates mapping on the fly from that field, and
  `_guess_chart_template()` uses it to pick a default CoA for a company's country.

This means introducing Libyz's VAT logic won't require editing any central registry —
a new `l10n_lz` module registering a template tagged with Libyz's `country_id` would be
picked up automatically.

### Do we need l10n_lz right away?

No — a bare `res.country` record (already added, id `lz`) is enough for Libyz to be usable
everywhere in the UI (addresses, company country, selection fields). What's missing without
a localization module is anything Accounting-related:
- No chart template has `country_id == lz`, so `ir.module.module.write()`'s auto-pick logic
  (`addons/account/models/ir_module.py:62-75`) falls back to the built-in `generic_coa`
  template (`addons/account/models/template_generic_coa.py`) when Accounting is set up for a
  Libyz company.
- `generic_coa` only registers chart-of-accounts data (`account.account`) and some company
  defaults (and even hardcodes `account_fiscal_country_id: base.us`) — it registers **no
  `account.tax` template at all**, so a Libyz company gets zero preconfigured VAT out of the box.
- Conclusion: fine for anything non-fiscal; not sufficient once we need real VAT behavior
  (and definitely not sufficient for the Tuesday-rate rule, which needs actual code).

### Anatomy of a country module / what a minimal l10n_lz needs

There is no `l10n_ly` (old Libya) module in this codebase to copy from. Checked other small
localization modules (`l10n_ee`, `l10n_om`, `l10n_bh`, ...) for the standard shape:
- `__manifest__.py`: `'countries': ['lz']`, `depends: ['account']`, `auto_install: ['account']`.
- `models/template_lz.py`: registers the chart template via the `@template('lz')` decorator
  (template data + `code_digits`) and `@template('lz', 'res.company')` (company defaults:
  fiscal country, account prefixes, default sale/purchase tax, etc.).
- `data/template/account.account-lz.csv`, `account.group-lz.csv`, `account.tax.group-lz.csv`,
  `account.tax-lz.csv`, `account.fiscal.position-lz.csv`: these are **not** listed in the
  manifest's `data` key — they're auto-discovered by filename convention (`_parse_csv` in
  `chart_template.py`, called from generic root `@template(model=...)` hooks defined once in
  core). A missing CSV is just skipped (`FileNotFoundError` caught silently), so a minimal
  module can omit any of these except account.account/account.tax.
- Language note: even Arabic-region modules (`l10n_om` etc.) keep `name` fields in English by
  default; translations live separately as `name@ar` columns or `i18n/*.po` files. So copying
  structure from any existing module is safe regardless of that country's language — Libyz's
  module simply omits the `i18n/` folder since no translation is needed.
- Key structural point: a per-weekday tax rate is not expressible in `account.tax` data alone
  (rates aren't date-conditional) — it needs a real Python override, analogous to how
  `l10n_ee/models/account_tax.py` overrides `account.tax` (though that file only adds an
  Estonia-specific reporting-code field, not rate computation — it's a structural example of
  *where* such logic lives, not a functional template for it).
