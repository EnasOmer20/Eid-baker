from odoo import models, fields, api
from datetime import timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    working_days_per_month = fields.Float('Working days/month', required=True,
                                          help='Used to calculate wage per day.')
    working_hours_per_day = fields.Float('Working hours/day', required=True)

    from datetime import timedelta
    from odoo import models, fields, api

    class YourContractModel(models.Model):
        _inherit = 'hr.contract'

        @api.model
        def check_contract_expiry(self):
            """Notify the employee and their manager via email and internal message before contract expiration"""
            today = fields.Date.today()
            config = self.env['ir.config_parameter'].sudo()
            notify_days_before = int(config.get_param('hr_contract.notify_days_contract',default=30))

            contracts = self.search([
                ('date_end', '!=', False),
                ('date_end', '=', today + timedelta(days=notify_days_before))
            ])
            print("*******************",notify_days_before)

            mail_template = self.env.ref('mail.template_contract_expiry_notification', raise_if_not_found=False)

            for contract in contracts:
                employee = contract.employee_id
                print("**********************************************", employee.name)
                manager = employee.parent_id  # Get the employee's manager

                message_body = (
                    f"🔔 Reminder: The contract of **{employee.name}** will expire on **{contract.date_end}**."
                )

                # Notify Employee in Chatter
                employee.message_post(
                    body=message_body,
                    subject="Contract Expiry Reminder",
                    message_type='notification',
                    partner_ids=[employee.user_id.partner_id.id] if employee.user_id else []
                )

                # Notify Manager in Chatter
                if manager and manager.user_id:
                    manager.message_post(
                        body=message_body,
                        subject="Employee Contract Expiry Reminder",
                        message_type='notification',
                        partner_ids=[manager.user_id.partner_id.id]
                    )

                # Send Email to Manager
                if manager and manager.work_email:
                    if mail_template:
                        mail_template.sudo().send_mail(
                            contract.id,
                            force_send=True,
                            email_values={'email_to': manager.work_email}
                        )
                    else:
                        # If no template, send a basic email
                        mail_values = {
                            'subject': f"Contract Expiry Alert: {employee.name}",
                            'body_html': f"<p>{message_body}</p>",
                            'email_to': manager.work_email,
                            'email_from': self.env.user.email or 'no-reply@yourcompany.com',
                        }
                        self.env['mail.mail'].sudo().create(mail_values).send()
