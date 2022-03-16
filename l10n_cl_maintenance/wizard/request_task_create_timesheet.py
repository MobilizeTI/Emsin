from odoo import api, fields, models
from datetime import datetime


class RequestTaskCreateTimesheet(models.TransientModel):
    _name = 'request.task.create.timesheet'
    _description = "Create Timesheet from request task"

    _sql_constraints = [('time_positive', 'CHECK(time_spent > 0)', 'The timesheet\'s time must be positive')]

    time_spent = fields.Float('Time', digits=(16, 2))
    description = fields.Char('Description')
    task_request_id = fields.Many2one(
        'maintenance.request.task', "Task", required=True,
        default=lambda self: self.env.context.get('active_id', None),
        help="Task for which we are creating a request maintenance",
    )

    # employee_id = fields.Many2one(
    #     comodel_name='hr.employee',
    #     string='Employee',
    #     required=True)
    #
    # task_request_employees = fields.Many2many('hr.employee',
    #                                           'wz_create_timesheet_rel',
    #                                           'wz_ct_id', 'employee_id', compute='_compute_task_request_employees')
    #
    # @api.depends('task_request_id', 'employee_id')
    # def _compute_task_request_employees(self):
    #     for rec in self:
    #         emp_ids = [rec.employee_id.id]
    #         aux_ids = rec.task_request_id.employee_additional_ids.ids
    #         emp_ids += aux_ids
    #         rec.task_request_employees = [(6, 0, emp_ids)]

    def save_timesheet(self):
        # se crea el parte de horas para empleado responsable
        self.task_request_id.user_timer_id.unlink()
        values = {
            'task_request_id': self.task_request_id.id,
            'employee_id': self.task_request_id.employee_id.id,
            'date': fields.Date.context_today(self),
            'name': self.description,
            'user_id': self.env.uid,
            'unit_amount': self.time_spent,
        }
        self.env['account.analytic.line'].sudo().create(values)

        # se crea el parte de horas para los empleados adicionales
        for emp in self.task_request_id.employee_additional_ids:
            values.update({
                'employee_id': emp.id
            })
            self.env['account.analytic.line'].sudo().create(values)

        return True
