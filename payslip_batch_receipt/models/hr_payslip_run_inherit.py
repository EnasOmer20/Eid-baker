from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    receipt_id = fields.Many2one('account.move', string="Receipt", readonly=True)  # New Field


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def done_payslip_run(self):
        """Override to generate a single receipt per company with the total net salary, including a due date."""
        super(HrPayslipRun, self).done_payslip_run()

        account_move_obj = self.env['account.move']
        payslips_by_company = {}

        # Group payslips by company
        for payslip in self.slip_ids:
            company = payslip.company_id
            if company not in payslips_by_company:
                payslips_by_company[company] = []
            payslips_by_company[company].append(payslip)

        # Process each company separately
        for company, payslips in payslips_by_company.items():
            partner = company.partner_id
            if not partner:
                raise ValidationError(f"Company {company.name} does not have a partner set.")

            total_net_amount = 0.0
            invoice_lines = []
            invoice_date = fields.Date.today()
            due_date = invoice_date  # You can modify this based on payment terms

            for payslip in payslips:
                salary_net_rule = payslip.line_ids.filtered(lambda line: line.code == 'NET')
                if not salary_net_rule:
                    raise ValidationError(f"No NET salary rule found for {payslip.employee_id.name}")

                net_amount = salary_net_rule.total
                salary_account = salary_net_rule.salary_rule_id.account_credit

                if not salary_account:
                    raise ValidationError(f"No salary account set for the NET rule in {payslip.employee_id.name}")

                total_net_amount += net_amount

                # Create invoice line for each payslip with due date
                invoice_lines.append((0, 0, {
                    'name': f'Net Salary for {payslip.employee_id.name}',
                    'quantity': 1,
                    'price_unit': net_amount,
                    'account_id': salary_account.id,
                    'date_maturity': due_date,  # Ensure due date is set
                }))

            # Create a single receipt for the company
            move_vals = {
                'move_type': 'out_receipt',
                'partner_id': partner.id,
                'ref': f'Payslip Receipt - {company.name} - {invoice_date}',
                'invoice_date': invoice_date,
                'invoice_line_ids': invoice_lines,
                'invoice_date_due': due_date,
                'currency_id': company.currency_id.id,  # Ensure the correct currency is set
            }
            move = account_move_obj.create(move_vals)

            # Link payslips to the generated receipt
            for payslip in payslips:
                payslip.write({'receipt_id': move.id})