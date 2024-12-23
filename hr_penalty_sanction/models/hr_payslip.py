from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HREmployeePayslip(models.Model):
    _inherit = 'hr.payslip'

    # Function to add penal sanction line under "Other Inputs" if applicable
    @api.model
    def create(self, vals):
        # Call the parent create method to ensure the payslip is created
        payslip = super(HREmployeePayslip, self).create(vals)

        penal_sanctions = self.env['hr.penal.sanction'].search([
            ('employee_id', '=', payslip.employee_id.id),
            ('date', '<=', payslip.date_to),
            ('date', '>=', payslip.date_from),
            ('is_salary_deduction', '=', True),
            ('state', '=', 'hr_confirmed')  # Ensure it is confirmed
        ])

        if penal_sanctions:
            # Add penal sanction lines under "Other Inputs"
            for sanction in penal_sanctions:
                if sanction.stage_id.deduction_type == 'fixed':
                    self.env['hr.payslip.input'].create({
                        'payslip_id': payslip.id,
                        'code': "PSD",
                        'name': 'Penal Sanction: ' + sanction.violation_id.name,
                        'amount': sanction.amount,
                    })
                elif sanction.stage_id.deduction_type == 'per_day':
                    self.env['hr.payslip.input'].create({
                        'payslip_id': payslip.id,
                        'code': "PSD",
                        'contract_id': payslip.contract_id.id,
                        'name': 'Penal Sanction: ' + sanction.violation_id.name,
                        'amount': payslip.contract_id.wage / payslip.contract_id.working_hours_per_day ,
                    })

        return payslip
