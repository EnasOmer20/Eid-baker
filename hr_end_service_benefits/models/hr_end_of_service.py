from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

def relativeDelta(enddate, startdate):
    if not startdate or not enddate:
        return relativedelta()
    startdate = fields.Datetime.from_string(startdate)
    enddate = fields.Datetime.from_string(enddate) + relativedelta(days=1)
    return relativedelta(enddate, startdate)

def delta_desc(delta):
    res = []
    if delta.years:
        res.append('%s Years' % delta.years)
    if delta.months:
        res.append('%s Months' % delta.months)
    if delta.days:
        res.append('%s Days' % delta.days)
    return ', '.join(res)

class HREndServiceRequest(models.Model):
    _name = 'hr.end.service'
    _description = 'End of Service Request'

    name = fields.Char(string="Request Name", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    hiring_date = fields.Date(related='employee_id.hiring_date', string="Hiring Date", store=True)
    service_date_years = fields.Float(string="Service Date [Years]",compute="_compute_service_date_in_years", store=True, required=True)
    years = fields.Float(string="Years", compute="_compute_service_date_in_years")
    months = fields.Float(string="Months", compute="_compute_service_date_in_years")
    days = fields.Float(string="Days", compute="_compute_service_date_in_years")
    reword_type = fields.Selection([('replacement', 'Replacement'), ('ending_service', 'Ending Service')], string="Reword Type", required=True)
    reason_id = fields.Many2one('hr.end.service.reason', string="Reason", required=True)
    date_request = fields.Date(string="Request Date", default=fields.Date.today)
    date_approval = fields.Date(string="Approval Date")
    date_payment = fields.Date(string="Payment Date")
    unpaid_leave_month = fields.Float('Unpaid Leave Months', compute='_compute_service_date_in_years', store=True)
    unpaid_leave_desc = fields.Char('Unpaid Leave', compute='_compute_service_date_in_years', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr_approval', 'HR Approval'),
        ('accounting', 'Accounting'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)
    total_deserved_amount = fields.Float(string="Total Deserved Amount", compute="_compute_total_amount", store=True)
    requested_amount = fields.Float(string="Requested Amount")
    notes = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('end.of.service') or 'New'
        return super(HREndServiceRequest, self).create(vals)

    @api.depends('hiring_date')
    def _compute_service_date_in_years(self):
        for record in self:
            if record.hiring_date:
                today = fields.Date.today()
                difference = relativedelta(today, record.hiring_date)
                unpaid_leave_delta = relativedelta()
                unpaid_leave_ids = self.env['hr.leave'].sudo().search([('employee_id', '=', record.employee_id.id),
                                                                       ('state', '=', 'validate'),
                                                                       ('holiday_status_id.unpaid', '=', True)])
                for leave_id in unpaid_leave_ids:
                    unpaid_leave_delta += relativeDelta(leave_id.date_to, leave_id.date_from)

                delta = relativeDelta(record.date_request, record.hiring_date)
                # record.service_desc = delta_desc(delta)

                delta -= unpaid_leave_delta

                record.unpaid_leave_desc = delta_desc(unpaid_leave_delta)
                record.unpaid_leave_month = (unpaid_leave_delta.years * 12) + (unpaid_leave_delta.months) + (unpaid_leave_delta.days / 30.0)

                # Calculate the total years including fractional years
                record.service_date_years = difference.years + (difference.months / 12.0)
                record.years = difference.years
                record.months = difference.months
                record.days = difference.days
            else:
                record.service_date_years = 0.0
                record.years = 0.0
                record.months = 0.0
                record.days = 0.0


    def action_submit(self):
        self.state = 'hr_approval'
        # Send email notification to HR Manager
        self.message_post(body=_("End of Service Request submitted for approval."))

    def action_approve_hr(self):
        self.state = 'accounting'
        # Notify accounting team
        self.message_post(body=_("HR Manager approved the request. Awaiting accounting processing."))

    def action_approve_accounting(self):
        self.state = 'done'
        # Archive employee and cancel contract
        self.employee_id.active = False
        self.message_post(body=_("Accounting approved the request. Process completed."))
