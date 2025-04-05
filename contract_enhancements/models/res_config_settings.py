from odoo import models, fields, api

class HrSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    notify_days_health_certificate = fields.Integer(string="Notify Days Before Health Certificate Expiry", default=30)
    notify_days_work_permit = fields.Integer(string="Notify Days Before Work Permit Expiry", default=30)
    notify_days_health_insurance = fields.Integer(string="Notify Days Before Health Insurance Expiry", default=30)
    notify_days_contract = fields.Integer(string="Notify Days Before Contract Expiry",related='company_id.notify_days_contract',readonly=False, default=30)

    def set_values(self):
        super(HrSettings, self).set_values()
        config = self.env['ir.config_parameter'].sudo()
        config.set_param('hr_employee.notify_days_health_certificate', self.notify_days_health_certificate)
        config.set_param('hr_employee.notify_days_work_permit', self.notify_days_work_permit)
        config.set_param('hr_employee.notify_days_health_insurance', self.notify_days_health_insurance)

    @api.model
    def get_values(self):
        res = super(HrSettings, self).get_values()
        config = self.env['ir.config_parameter'].sudo()
        res.update(
            notify_days_health_certificate=int(config.get_param('hr_employee.notify_days_health_certificate', default=30)),
            notify_days_work_permit=int(config.get_param('hr_employee.notify_days_work_permit', default=30)),
            notify_days_health_insurance=int(config.get_param('hr_employee.notify_days_health_insurance', default=30)),
        )
        return res
