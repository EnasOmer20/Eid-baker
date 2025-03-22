from odoo import models, fields, api
from datetime import timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    health_certificate = fields.Binary(string="Health Certificate", attachment=True)
    health_certificate_expiry = fields.Date(string="Health Certificate Expiry Date")
    health_certificate_name = fields.Char(string="Health Certificate Name")

    health_insurance = fields.Binary(string="Health Insurance", attachment=True)
    health_insurance_expiry = fields.Date(string="Health Insurance Expiry Date")
    health_insurance_name = fields.Char(string="Health Insurance Name")


    @api.model
    def check_expiry_dates(self):
        today = fields.Date.today()
        config = self.env['ir.config_parameter'].sudo()

        notify_days_health_certificate = int(config.get_param('hr_employee.notify_days_health_certificate', default=30))
        notify_days_work_permit = int(config.get_param('hr_employee.notify_days_work_permit', default=30))
        notify_days_health_insurance = int(config.get_param('hr_employee.notify_days_health_insurance', default=30))

        employees = self.search([])

        for employee in employees:
            message_body = "Reminder: The following documents will expire soon:\n"
            notify = False

            if employee.health_certificate_expiry and employee.health_certificate_expiry <= today + timedelta(
                    days=notify_days_health_certificate):
                message_body += f"✅ Health Certificate: {employee.health_certificate_expiry}\n"
                notify = True
            if employee.work_permit_expiration_date and employee.work_permit_expiration_date <= today + timedelta(
                    days=notify_days_work_permit):
                message_body += f"✅ Work Permit: {employee.work_permit_expiration_date}\n"
                notify = True
            if employee.health_insurance_expiry and employee.health_insurance_expiry <= today + timedelta(
                    days=notify_days_health_insurance):
                message_body += f"✅ Health Insurance: {employee.health_insurance_expiry}\n"
                notify = True

            if notify:
                employee.message_post(body=message_body, subject="Document Expiry Reminder")
