# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('lz')
    def _get_lz_template_data(self):
        return {
            'property_account_receivable_id': 'l10n_lz_receivable',
            'property_account_payable_id': 'l10n_lz_payable',
            'code_digits': '6',
        }

    @template('lz', 'res.company')
    def _get_lz_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.lz',
                'bank_account_code_prefix': '100',
                'cash_account_code_prefix': '101',
                'transfer_account_code_prefix': '105',
                'income_account_id': 'l10n_lz_income',
                'expense_account_id': 'l10n_lz_expense',
                'account_sale_tax_id': 'l10n_lz_sale_vat',
                'account_purchase_tax_id': 'l10n_lz_purchase_vat',
            },
        }
