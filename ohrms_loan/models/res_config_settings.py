from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_account_id = fields.Many2one(
        'account.account', string="Loan Account",
        domain="[('deprecated', '=', False)]",
        related='company_id.loan_account_id',
        readonly=False,
    )
    loan_journal_id = fields.Many2one(
        'account.journal', string="Loan Journal",
        related='company_id.loan_journal_id',
        readonly=False,
    )

class ResCompany(models.Model):
    _inherit = 'res.company'

    loan_account_id = fields.Many2one(
        'account.account', string="Loan Account",
        domain="[('deprecated', '=', False)]",
        help="Account used for recording loan transactions.",
        company_dependent=True,
    )
    loan_journal_id = fields.Many2one(
        'account.journal', string="Loan Journal",
        domain="[('type', '=', 'sale')]",
        help="Journal used for recording loan receipts.",
        company_dependent=True,
    )