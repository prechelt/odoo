# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# TODO: this file is a placeholder, copied from l10n_ee/models/account_tax.py.
# It only demonstrates *where* a country-specific account.tax override lives
# in a localization module. Its content below (an Estonian VAT-report code
# field) is not relevant to Libyz and must be replaced by the actual
# weekday-dependent VAT rate logic (lower rate on Tuesdays) once that has
# been specified.

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_lz_kmd_inf_code = fields.Selection(
        selection=[
            ('1', 'Sale KMS §41/42'),
            ('2', 'Sale KMS §41^1'),
            ('11', 'Purchase KMS §29(4)/30/32'),
            ('12', 'Purchase KMS §41^1'),
        ],
        string='KMD INF Code',
        default=False,
        help='This field is used for the comments/special code column in the KMD INF report.'
    )
