# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, date_utils
import datetime


class MaintenanceRequestTaskStage(models.Model):
    _name = 'maintenance.request.task.stage'
    _description = 'Task Stage'
    _order = 'sequence, id'

    def _get_default_request_ids(self):
        default_request_id = self.env.context.get('default_request_id')
        return [default_request_id] if default_request_id else None

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Stage Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    require_valid_picking = fields.Boolean("Require Validate Pickings")

    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    request_ids = fields.Many2many('maintenance.request',
                                   'request_task_type_rel',
                                   'type_id',
                                   'request_id',
                                   string='requests',
                                   default=_get_default_request_ids)
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'request.task')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    rating_template_id = fields.Many2one(
        'mail.template',
        string='Rating Email Template',
        domain=[('model', '=', 'request.task')],
        help="If set and if the request's rating configuration is 'Rating when changing stage', then an email will be sent to the customer when the task reaches this step.")
    auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False,
                                                  help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
                                                       " * A good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
                                                       " * A medium or a bad feedback will set the kanban state to 'blocked' (red bullet).\n")
    is_closed = fields.Boolean('Closing Stage', help="Tasks in this stage are considered as closed.")
    disabled_rating_warning = fields.Text(compute='_compute_disabled_rating_warning')

    def unlink_wizard(self, stage_view=False):
        self = self.with_context(active_test=False)
        # retrieves all the requests with a least 1 task in that stage
        # a task can be in a stage even if the request is not assigned to the stage
        readgroup = self.with_context(active_test=False).env['maintenance.request.task'].read_group(
            [('stage_id', 'in', self.ids)],
            ['request_id'], ['request_id'])
        request_ids = list(set([request['request_id'][0] for request in readgroup] + self.request_ids.ids))

        wizard = self.with_context(request_ids=request_ids).env['rt.stage.delete.wizard'].create({
            'request_ids': request_ids,
            'stage_ids': self.ids
        })

        context = dict(self.env.context)
        context['stage_view'] = stage_view
        return {
            'name': _('Delete Stage'),
            'view_mode': 'form',
            'res_model': 'rt.stage.delete.wizard',
            'views': [
                (self.env.ref('l10n_cl_maintenance.rt_stage_delete_wz_view_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': wizard.id,
            'target': 'new',
            'context': context,
        }

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            self.env['maintenance.request.task'].search([('stage_id', 'in', self.ids)]).write({'active': False})
        return super(MaintenanceRequestTaskStage, self).write(vals)

    # @api.onchange('stage_id')
    # def onchange_stage_id(self):

    @api.depends('request_ids')
    def _compute_disabled_rating_warning(self):
        for stage in self:
            disabled_requests = stage.request_ids
            if disabled_requests:
                stage.sudo().disabled_rating_warning = '\n'.join('- %s' % p.name for p in disabled_requests)
            else:
                stage.sudo().disabled_rating_warning = False

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The task stage name must be unique!'),
    ]


# class MaintenanceRequestTaskStage(models.Model):
#     _name = 'maintenance.request.task.stage'
#     _order = 'sequence,name'
#
#     name = fields.Char()
#     sequence = fields.Integer()
#     fold = fields.Boolean()
#     description = fields.Text(translate=True)
#     request_state = fields.Selection(
#         [('draft', 'To do'),
#          ('done', 'Done'),
#          ('cancel', 'Cancel'),
#          ],
#         'State', default="draft")


class MaintenanceRequestTask(models.Model):
    _name = 'maintenance.request.task'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'timer.mixin', 'rating.mixin']
    _description = 'Maintenance Request Task'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Name_seq', required=False)
    flag_create_task = fields.Boolean(string='Flag create task from request', required=False)
    flag_from_request = fields.Boolean(string='Flag_from_request', required=False)

    active = fields.Boolean(default=True)
    color = fields.Integer()

    sequence = fields.Integer(default=1)
    planned_date_begin = fields.Datetime("Start date")
    planned_date_end = fields.Datetime("End date")
    flag_timer = fields.Boolean(compute='_compute_flag_timer')

    @api.depends('planned_date_begin', 'planned_date_end')
    def _compute_flag_timer(self):
        for rec in self:
            rec.sudo().flag_timer = rec.display_timer_start_secondary or not (
                    rec.planned_date_begin and rec.planned_date_end) or rec.encode_uom_in_days

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Priority")

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)

    @api.model
    def _default_rent_stage(self):
        Stage = self.env['maintenance.request.task.stage']
        return Stage.search([], limit=1)

    @api.model
    def _group_expand_stages(self, stages, domain, order):
        return stages.search([], order=order)

    stage_id = fields.Many2one(
        'maintenance.request.task.stage',
        default=_default_rent_stage,
        group_expand='_group_expand_stages'
    )

    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True,
                                 related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True,
                              related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True,
                                related_sudo=False)
    is_closed = fields.Boolean(related="stage_id.is_closed",
                               string="Closing Stage", readonly=True, related_sudo=False)

    description = fields.Html(string='Description')
    allowed_user_ids = fields.Many2many('res.users', string="Visible to")
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True)
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
                                             index=True,
                                             copy=False,
                                             readonly=True)

    duration_compute = fields.Float(compute='_compute_duration_compute')

    @api.depends('activity_id')
    def _compute_duration_compute(self):
        for request in self:
            request.sudo().duration_compute = 0
            if request.activity_id:
                request.sudo().duration_compute = request.activity_id.duration
                if request.planned_hours == 0:
                    request.sudo().planned_hours = request.activity_id.duration

    planned_hours = fields.Float("Initially Planned Hours",
                                 help='Time planned to achieve this task (including its sub-tasks).', tracking=True)

    effective_hours = fields.Float("Hours Spent", compute='_compute_effective_hours', compute_sudo=True, store=True,
                                   help="Time spent on this task, excluding its sub-tasks.")
    total_hours_spent = fields.Float("Total Hours", compute='_compute_total_hours_spent', store=True,
                                     help="Time spent on this task, including its sub-tasks.")
    progress = fields.Float("Progress",
                            compute='_compute_progress_hours',
                            store=True, group_operator="avg",
                            help="Display progress of current task.")

    overtime = fields.Float(compute='_compute_progress_hours', store=True)

    @api.depends('effective_hours', 'planned_hours')
    def _compute_progress_hours(self):
        for task in self:
            if (task.planned_hours > 0.0):
                task_total_hours = task.effective_hours
                task.sudo().overtime = max(task_total_hours - task.planned_hours, 0)
                if task_total_hours > task.planned_hours:
                    task.sudo().progress = 100
                else:
                    task.sudo().progress = round(100.0 * task_total_hours / task.planned_hours, 2)
            else:
                task.sudo().progress = 0.0
                task.sudo().overtime = 0

    activity_id = fields.Many2one('guideline.activity', 'Activity')
    activity_speciality_ids = fields.Many2many(related='activity_id.specialty_tag_ids')
    # data relacionada
    activity_system_class_id = fields.Many2one('maintenance.system.classification',
                                               related='activity_id.system_class_id', string='Component')
    activity_duration = fields.Float(related='activity_id.duration', help="Duration in hours.")

    activity_att_documents = fields.Many2many('ir.attachment', string='Documents', related='activity_id.att_documents')
    activity_description = fields.Html(string='Description task', related='activity_id.description')

    activity_url_ids = fields.One2many('activity.url', 'activity_id', 'Urls', related='activity_id.url_ids')
    activity_url_video = fields.Char(string='Url video', related='activity_id.url_video')

    employee_id = fields.Many2one('hr.employee', 'Employee',
                                  required=False, check_company=True)

    user_id = fields.Many2one(related='employee_id.user_id', store=True)

    # empleados adicionales
    employee_additional_ids = fields.Many2many('hr.employee', string='Employees additional')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.update(dict(date_assign=fields.Datetime.now()))

    request_id = fields.Many2one(
        'maintenance.request',
        string='Request', ondelete='cascade',
        required=True)

    request_equipment_id = fields.Many2one('maintenance.equipment',
                                           string='Equipment', related='request_id.equipment_id')

    request_speciality_ids = fields.Many2many(related='request_id.guideline_speciality_ids',
                                              string='request_speciality_ids')

    timesheet_ids = fields.One2many('account.analytic.line', 'task_request_id', 'Timesheets')

    @api.constrains("stage_id")
    def _check_task_dependent(self):
        if self.activity_id.parent_id and self.stage_id.name != 'Por Hacer':
            task_dependent = self.search(
                [('activity_id', '=', self.activity_id.parent_id.id), ('request_id', '=', self.request_id.id)])
            if task_dependent and task_dependent.stage_id.name != 'Hecho':
                raise ValidationError(_(f'Task {task_dependent.name} pending validation'))

    def action_draft(self):
        pass

    #     self.ensure_one()
    #     tasks_request = self.search([('request_id', '=', self.request_id.id)])
    #     for task in tasks_request:
    #         if self.activity_id.name in task.activity_id.complete_name:
    #             task.state = 'draft'

    def action_confirm(self):
        pass
        # self.ensure_one()

    display_timesheet_timer = fields.Boolean("Display Timesheet Time", compute='_compute_display_timesheet_timer')

    display_timer_start_secondary = fields.Boolean(compute='_compute_display_timer_buttons')

    @api.depends('display_timesheet_timer', 'timer_start', 'timer_pause', 'total_hours_spent')
    def _compute_display_timer_buttons(self):
        for task in self:
            if not task.display_timesheet_timer:
                task.update({
                    'display_timer_start_primary': False,
                    'display_timer_start_secondary': False,
                    'display_timer_stop': False,
                    'display_timer_pause': False,
                    'display_timer_resume': False,
                })
            else:
                super(MaintenanceRequestTask, task)._compute_display_timer_buttons()
                task.sudo().display_timer_start_secondary = task.display_timer_start_primary
                if not task.timer_start:
                    task.update({
                        'display_timer_stop': False,
                        'display_timer_pause': False,
                        'display_timer_resume': False,
                    })
                    if not task.total_hours_spent:
                        task.display_timer_start_secondary = False
                    else:
                        task.display_timer_start_primary = False

        # @api.depends()

    def _compute_display_timesheet_timer(self):
        for task in self:
            task.sudo().display_timesheet_timer = True

    def action_timer_start(self):
        if not self.user_timer_id.timer_start:
            super(MaintenanceRequestTask, self).action_timer_start()

    def action_timer_stop(self):
        # timer was either running or paused
        if self.user_timer_id.timer_start and self.display_timesheet_timer:
            minutes_spent = self.user_timer_id._get_minutes_spent()
            # minimum_duration = int(
            #     self.env['ir.config_parameter'].sudo().get_param('hr_timesheet.timesheet_min_duration', 0))
            # rounding = int(self.env['ir.config_parameter'].sudo().get_param('hr_timesheet.timesheet_rounding', 0))
            # minutes_spent = self._timer_rounding(minutes_spent, minimum_duration, rounding)
            return self._action_open_new_timesheet(minutes_spent * 60 / 3600)
        return False

    def _action_open_new_timesheet(self, time_spent):
        return {
            "name": _("Confirm Time Spent"),
            "type": 'ir.actions.act_window',
            "res_model": 'request.task.create.timesheet',
            "views": [[False, "form"]],
            "target": 'new',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': self._name,
                'default_time_spent': time_spent,
            },
        }

    @api.model
    def create(self, values):
        # Add code here
        if values.get('name', _('New')) == _('New'):
            name_seq = self.env['ir.sequence'].next_by_code('mtn.request.sequence')
            name = name_seq
            name_seq = name_seq
            if 'activity_id' in values:
                activity_id = self.activity_id.browse(values.get('activity_id'))
                name = f'{activity_id.name} [{name_seq}]'
            values.update(dict(name=name, name_seq=name_seq))
        task = super(MaintenanceRequestTask, self).create(values)
        # if task.stage_id.request_state:
        #     task.book_id.state = rent.stage_id.book_state
        return task

    def write(self, values):
        # Add code here
        if 'activity_id' in values:
            activity_id = self.activity_id.browse(values.get('activity_id'))
            name = f'{activity_id.name} ({self.name_seq})'
            values.update(dict(name=name, name_seq=self.name_seq))
        rec = super(MaintenanceRequestTask, self).write(values)
        flag_update_picking_from_task = self._context.get('flag_update_picking_from_task', False)
        if 'stage_id':
            tasks = self.search([('request_id', '=', self.request_id.id)])
            tasks_aux = tasks.filtered(lambda l: l.stage_id.name == 'Por Hacer')
            if len(tasks_aux) == 0 and values and flag_update_picking_from_task:
                if self.request_id.flag_validate_auto:
                    # se marca la solicitud como reparada
                    self.request_id.stage_id = self.env.ref('maintenance.stage_3').id
            # elif self.request_id.stage_id.name not in ('Nueva solicitud', 'Para Reparar'):
            #     self.request_id.stage_id = self.env.ref('maintenance.stage_1').id

        return rec

    @api.depends('timesheet_ids.unit_amount')
    def _compute_effective_hours(self):
        for task in self:
            task.sudo().effective_hours = round(sum(task.timesheet_ids.mapped('unit_amount')), 2)

    @api.depends('effective_hours')
    def _compute_total_hours_spent(self):
        for task in self:
            task.sudo().total_hours_spent = task.effective_hours

    encode_uom_in_days = fields.Boolean(compute='_compute_encode_uom_in_days')

    def _compute_encode_uom_in_days(self):
        self.sudo().encode_uom_in_days = self.env.company.timesheet_encode_uom_id == self.env.ref('uom.product_uom_day')

    # asignación de empleado masivo
    def action_massive_employee_update(self):
        request_task_ids = self.env.context.get('active_ids', [])
        view = self.env.ref('l10n_cl_maintenance.mtm_request_task_wz_form_view')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['default_task_ids'] = [(6, 0, request_task_ids)]
        return {
            'name': 'Asignación Masiva de Empleado',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mtm.request.task.wz',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }

        # security resticción
    flag_readonly = fields.Boolean(
        string='flag_readonly',
        compute='_compute_flag_readonly')

    @api.depends('user_id')
    def _compute_flag_readonly(self):
        for record in self:
            flag_readonly = False
            user = record.env.user
            if user.has_group('l10n_cl_maintenance.group_tecnicos'):
                flag_readonly = True
            record.flag_readonly = flag_readonly


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    task_request_id = fields.Many2one('maintenance.request.task', 'Task Request')
    flag_req_account_id = fields.Boolean(default=True)
    account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                 required=False, ondelete='restrict', index=True, check_company=True)

    datetime_create_line = fields.Datetime(
        string='datetime_create_ot',
        compute='_compute_datetime_create_line')

    @api.depends('create_date')
    def _compute_datetime_create_line(self):
        for rec in self:
            if rec.create_date:
                user_tz = pytz.timezone(self.env.user.tz or 'America/Bogota')
                time_in_timezone = pytz.utc.localize(rec.create_date).astimezone(user_tz)
                rec.datetime_create_line = time_in_timezone.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                rec.datetime_create_line = False

    datetime_start = fields.Datetime(
        string='datetime_start',
        compute='_compute_datetime_start')

    @api.depends('datetime_create_line', 'unit_amount')
    def _compute_datetime_start(self):
        for rec in self:
            if rec.datetime_create_line and rec.unit_amount:
                session_start = fields.Datetime.from_string(rec.datetime_create_line)
                interval = datetime.timedelta(seconds=(rec.unit_amount * 3600))
                rec.datetime_start = fields.Datetime.to_string(session_start - interval)
            else:
                rec.datetime_start = False

    # rt_employee_id = fields.Many2one('hr.employee')

    # reset amount on copy
    # amount = fields.Monetary(copy=False)
    # validated = fields.Boolean("Validated line", group_operator="bool_and", store=True, copy=False)

    @api.onchange('task_request_id')
    def onchange_task_request_id(self):
        self.update(dict(employee_id=self.task_request_id.employee_id.id))


