# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning, UserError


class MaintenanceGuidelineType(models.Model):
    _name = 'maintenance.guideline.type'
    _description = 'Maintenance Guideline Type'

    name = fields.Char('Name', required=True)
    prefix = fields.Char(help="Prefix value of the record for Maintenance Guideline", trim=False)
    suffix = fields.Char(help="Suffix value of the record for Maintenance Guideline", trim=False)
    preview = fields.Char(compute='_compute_preview')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('name', 'prefix', 'suffix')
    def _compute_preview(self):
        for record in self:
            record.preview = ("%s xxxx yyyy" % ' '.join(filter(None, [
                record.prefix or '',
                record.name or '',
                record.suffix or ''
            ]))).strip()


class MaintenanceGuideline(models.Model):
    _name = 'maintenance.guideline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Maintenance Guideline General'
    _check_company_auto = True

    name = fields.Char('Name', required=True)
    display_name = fields.Char(compute="_compute_display_name")

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    description = fields.Text('Description')
    guideline_type_id = fields.Many2one('maintenance.guideline.type',
                                        'Guideline Type', ondelete='restrict',
                                        required=True, check_company=True)

    maintenance_type = fields.Selection(
        string=' Maintenance type',
        selection=[('preventive', 'Preventive'),
                   ('corrective', 'Corrective'), ],
        required=True, default='preventive')
    maintenance_duration = fields.Float(string='Duration', help="Maintenance Duration in hours.")

    equipment_ids = fields.Many2many('maintenance.equipment',
                                     'maintenance_guideline_equipment_rel',
                                     'mtn_equipment_id', 'mtn_guideline_id',
                                     string='Equipments')

    equipment_activity_id = fields.Many2one('maintenance.equipment.activity',
                                            'Equipment Activity',
                                            check_company=True)
    equipment_activity_uomctg_id = fields.Many2one('uom.category', 'Equipment Activity UoM Category',
                                                   related='equipment_activity_id.uom_id.category_id',
                                                   readonly=True, store=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure',
                             domain="[('category_id', '=', equipment_activity_uomctg_id)]")

    measurement = fields.Selection([
        ('fixed', 'At reached value'),
        ('frequently', 'Frequently'),
    ], 'Measurement', default='frequently')
    period = fields.Integer('Frequency', help='Frequency between each preventive maintenance')
    percentage_def = fields.Float(
        string='Percentage',
        default=0.9,
        help='Percentage that must be met in order to execute the guideline automatically ')
    percentage_value = fields.Float(
        string='Percentage value',
        compute='_compute_percentage_value')

    ot_template_id = fields.Many2one(comodel_name='ot.template',
                                     string='OT template',
                                     required=False)

    flag_create_auto = fields.Boolean(string='Automatic planning?', required=False)
    flag_execute_auto = fields.Boolean(string='Automatic execute planning', required=False)

    type_auto_planning = fields.Selection(
        string='Planning type',
        selection=[('latest', 'Last Record'),
                   ('accumulated', 'Accumulated Record'), ],
        default='latest',
        help="Latest: About the last recorded odometer in history\n"
             "Accumulated: About the accumulated vehicle odometer"
    )

    value = fields.Integer('Value')

    @api.depends('period', 'value', 'percentage_def')
    def _compute_percentage_value(self):
        for rec in self:
            rec.percentage_value = 0.0
            if rec.measurement == 'frequently':
                if rec.period and rec.percentage_def:
                    x = (rec.percentage_def * 100 * rec.period) / 100
                    rec.percentage_value = x
            else:
                if rec.value and rec.percentage_def:
                    x = (rec.percentage_def * 100 * rec.value) / 100
                    rec.percentage_value = x

    att_documents = fields.Many2many('ir.attachment', string='Documents', required=False)
    url_ids = fields.One2many('guideline.url', 'guideline_id', 'Urls', copy=True, auto_join=True)

    activities_ids = fields.One2many('maintenance.guideline.activity', 'guideline_id',
                                     'Detail Activities', copy=True,
                                     auto_join=True)

    bool_in_request = fields.Boolean(string='Bool in request', required=False, copy=False)

    @api.depends('guideline_type_id', 'uom_id', 'measurement', 'period', 'value')
    def _compute_name(self):
        for record in self:
            record.name = ('%s %s %s' % (
                ' '.join(filter(None, [
                    record.guideline_type_id.prefix or '',
                    record.guideline_type_id.name or '',
                    record.guideline_type_id.suffix or '',
                ])),
                record.period if record.measurement == 'frequently' else record.value,
                record.uom_id.name or '',
            )).strip()

    @api.onchange('equipment_activity_id')
    def _onchange_equipment_activity(self):
        if self.equipment_activity_id:
            self.uom_id = self.equipment_activity_id.uom_id

    @api.onchange('measurement')
    def _onchange_measurement(self):
        if self.measurement == 'frequently':
            self.value = False
        else:
            self.value = self.period
            self.percentage_def = 1.0

    @api.constrains('period', 'value')
    def _check_maintenance_measurement(self):
        invalid_records = self.filtered(lambda r: not r.period and not r.value and r.maintenance_type == 'preventive')

        if invalid_records:
            raise ValidationError(_(
                "The following %s %s don't have value either for frequently or fixed measurement"
            ) % (
                                      ',\n '.join(invalid_records.mapped('display_name')),
                                      _(self._description),
                                  ))

    @api.constrains('uom_id', 'equipment_activity_uomctg_id')
    def _check_uom_category(self):
        invalid_records = self.filtered(lambda r: r.uom_id.category_id != r.equipment_activity_uomctg_id)
        if invalid_records:
            raise ValidationError(_(
                "The following %s %s don't have the correct unit of measurement category"
            ) % (
                                      ',\n '.join(invalid_records.mapped('display_name')),
                                      _(self._description),
                                  ))

    @api.model
    def create(self, values):
        # Add code here
        res = super(MaintenanceGuideline, self).create(values)
        self.env.context = dict(self.env.context)

        bool_logic = self._context.get('bool_logic', False)
        if res.activities_ids and not bool_logic:
            set_activity = set()
            data_activities = []
            for line in res.activities_ids:
                act_ids = line.activity_id.parent_path.split('/')
                act_ids = act_ids[::-1]
                for ac_id in act_ids:
                    if ac_id and int(ac_id):
                        if ac_id not in set_activity:
                            data_activities.append((0, 0, dict(activity_id=int(ac_id),
                                                               system_class_id=line.system_class_id.id,
                                                               guideline_id=res.id)))
                            set_activity.add(ac_id)
            if data_activities:
                res.sudo().write(dict(activities_ids=[(6, 0, [])]))
                res.sudo().write(dict(activities_ids=data_activities))
        if 'equipment_ids' in values:
            aux_ids = values.get('equipment_ids', [])
            ids = []
            for aux in aux_ids:
                ids += aux[2]
            equipment_ids = res.env['maintenance.equipment'].browse(ids)
            for equipment in equipment_ids:
                if res not in equipment.maintenance_guideline_ids:
                    self.env.context.update({'flag_update_from_guideline': True})
                    equipment.sudo().maintenance_guideline_ids = [(4, res.id)]
        return res

    def write(self, values):
        # Add code here
        res = super(MaintenanceGuideline, self).write(values)
        self.env.context = dict(self.env.context)
        bool_update_activities = self._context.get('bool_update_activities', False)
        if 'activities_ids' in values and not bool_update_activities:
            set_activity = set()
            data_activities = []
            for line in self.activities_ids:
                act_ids = line.activity_id.parent_path.split('/')
                act_ids = act_ids[::-1]
                for ac_id in act_ids:
                    if ac_id and int(ac_id):
                        if ac_id not in set_activity:
                            new_line = self.env['maintenance.guideline.activity'].sudo().create(
                                dict(activity_id=int(ac_id),
                                     system_class_id=line.system_class_id.id,
                                     guideline_id=self.id))
                            data_activities.append(new_line.id)
                            set_activity.add(ac_id)

            self.env.context.update({'bool_update_activities': True})
            self.sudo().write(dict(activities_ids=[(6, 0, data_activities)]))
            return res
        flag_update_from_equipment = self._context.get('flag_update_from_equipment', False)
        if 'equipment_ids' in values and not flag_update_from_equipment:
            aux_ids = values.get('equipment_ids', [])
            ids = []
            for aux in aux_ids:
                ids += aux[2]
            equipment_ids = self.env['maintenance.equipment'].browse(ids)
            for equipment in equipment_ids:
                if self not in equipment.maintenance_guideline_ids:
                    self.env.context.update({'flag_update_from_guideline': True})
                    equipment.sudo().maintenance_guideline_ids = [(4, self.id)]

            equipment_all = self.env['maintenance.equipment'].search([])
            equipment_guidelines = equipment_all.filtered(lambda p: self in p.maintenance_guideline_ids)
            if equipment_guidelines:
                equipment_delete = list(set(equipment_guidelines) - set(equipment_ids))

                self.env.context.update({'flag_update_from_guideline': True})
                for e in equipment_delete:
                    e.sudo().maintenance_guideline_ids = [(3, self.id)]

        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
        except ValueError:
            default['name'] = self.name
        return super(MaintenanceGuideline, self).copy(default)


class ActivityUrl(models.Model):
    _name = 'guideline.url'
    _description = 'Guideline url'

    guideline_id = fields.Many2one('maintenance.guideline', string='Guideline', required=True, ondelete='cascade',
                                   index=True, copy=False)
    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description', required=False)


class MaintenanceGuidelineActivity(models.Model):
    _name = 'maintenance.guideline.activity'
    _description = 'Maintenance Guideline Activity'
    _check_company_auto = True

    sequence = fields.Integer(required=True, default=10)
    guideline_id = fields.Many2one('maintenance.guideline',
                                   string='Guideline',
                                   required=False,
                                   ondelete='cascade',
                                   index=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', related='guideline_id.company_id')

    activity_id = fields.Many2one('guideline.activity',
                                  string='Activity', required=True)

    system_class_id = fields.Many2one(
        'maintenance.system.classification',
        domain=[('allocation_level', '=', True)],
        string='Component',
        required=False)

    @api.onchange('activity_id')
    def onchange_activity_id(self):
        self.system_class_id = self.activity_id.system_class_id.id

    activity_att_documents = fields.Many2many(related='activity_id.att_documents')

    activity_code = fields.Char(related='activity_id.code', string='Code')
    activity_url_video = fields.Char(related='activity_id.url_video')
    activity_speciality_ids = fields.Many2many(related='activity_id.specialty_tag_ids')

    def action_open_url_video(self):
        self.ensure_one()
        if self.activity_url_video:
            return {
                'type': 'ir.actions.act_url',
                'url': self.activity_url_video,
                'target': 'new',
            }
        else:
            raise Warning(_(f'the activity does not have an assigned video'))

    def action_delete_custom(self):
        len_parent_path = self.activity_id.parent_path.split('/')

        if len(len_parent_path) == 2:
            view = self.env.ref('l10n_cl_maintenance.guideline_line_confirm_form_view')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['default_guideline_id'] = self.guideline_id.id
            context['default_line_guideline'] = self.id
            context[
                'default_text_message'] = 'Al eliminar esta actividad se eliminarán las actividades dependencias.'

            return {
                'name': _('Confirm'),
                'type': 'ir.actions.act_window',
                'res_model': 'guideline.line.confirm',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }
        else:
            self.unlink()


"""
    def unlink(self):
        bool_unlink_line = self._context.get('bool_unlink_line', False)
        ids = []
        if not bool_unlink_line:
            for rec in self:
                my_id = f'/{self.activity_id.id}/'
                more_guidelines = rec.guideline_id.activities_ids
                to_delete = more_guidelines.filtered(
                    lambda i: my_id in i.activity_id.parent_path_ids and i.id != rec.id)
                self.env.context = dict(self.env.context)
                self.env.context.update({'bool_unlink_line': True})
                ids += to_delete.ids

        if len(ids) > 0:
            self = self.with_context({
                'bool_unlink_line': True,
            })
            self.search([('id', 'in', ids)]).unlink()
        res = super(MaintenanceGuidelineActivity, self).unlink()
        return res

"""
