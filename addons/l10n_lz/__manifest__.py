# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Libyz - Accounting',
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'countries': ['lz'],
    'description': """
Libyz - Accounting (minimal development scaffold)
==================================================

This module is intentionally minimal, for development purposes only. It is NOT
feature-complete:

- data/template/account.tax-lz.csv defines a single flat placeholder VAT rate.
  It must be replaced once the actual Libyz VAT rule (lower rate on Tuesdays)
  has been specified and implemented.
- models/account_tax.py is a copy of l10n_ee's account.tax override, kept only
  to show *where* a country-specific account.tax override lives. Its content
  is Estonia-specific and must be replaced.
    """,
    'depends': ['account'],
    'auto_install': ['account'],
    'license': 'LGPL-3',
}
