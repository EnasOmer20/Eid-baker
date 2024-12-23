# -*- coding: utf-8 -*-


from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    working_days_per_month = fields.Float('Working days/month', help='Using to calculate wage/day.',required=True)

    working_hours_per_day = fields.Float('Working hours/day' ,required=True)
