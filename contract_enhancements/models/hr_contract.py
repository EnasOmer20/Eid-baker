from odoo import models, fields, api
from datetime import timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    working_days_per_month = fields.Float('Working days/month', required=True,
                                          help='Used to calculate wage per day.')
    working_hours_per_day = fields.Float('Working hours/day', required=True)

    @api.model
    def check_contract_expiry(self):
        """Notify the employee and their manager via email before contract expiration"""
        today = fields.Date.today()
        notify_days_before = int(self.env['ir.config_parameter'].sudo().get_param(
            'hr_employee.notify_days_contract', default=30
        ))

        contracts = self.search([
            ('date_end', '!=', False),
            ('date_end', '<=', today + timedelta(days=notify_days_before))
        ])

        mail_template = self.env.ref('mail.template_contract_expiry_notification', raise_if_not_found=False)

        for contract in contracts:
            employee = contract.employee_id
            manager = employee.parent_id  # Get the employee's manager

            message_body = (
                f"🔔 Reminder: The contract of **{employee.name}** will expire on **{contract.date_end}**."
            )

            # Notify Employee in Chatter
            employee.message_post(body=message_body, subject="Contract Expiry Reminder")

            # Send Email to Manager
            if manager and manager.work_email:
                if mail_template:
                    mail_template.sudo().send_mail(contract.id, force_send=True, email_values={'email_to': manager.work_email})
                else:
                    # If no template, send a basic email
                    mail_values = {
                        'subject': f"Contract Expiry Alert: {employee.name}",
                        'body_html': f"<p>{message_body}</p>",
                        'email_to': manager.work_email,
                        'email_from': self.env.user.email or 'no-reply@yourcompany.com',
                    }
                    self.env['mail.mail'].sudo().create(mail_values).send()
