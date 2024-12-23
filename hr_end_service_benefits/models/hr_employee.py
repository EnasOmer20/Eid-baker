from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hiring_date = fields.Date(string="Hiring Date", required=True)

