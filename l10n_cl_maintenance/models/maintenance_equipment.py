# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class MaintenanceEquipmentActivityTracking(models.Model):
    _name = 'maintenance.equipment.activity.tracking'
    _description = 'Maintenance Equipment Activity Tracking'

    _check_company_auto = True

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    equipment_id = fields.Many2one('maintenance.equipment',
                                   string='Equipment',
                                   ondelete='cascade',
                                   index=True,
                                   check_company=True)
    equipment_activity_id = fields.Many2one('maintenance.equipment.activity',
                                            'Equipment Activity', required=True,
                                            check_company=True)
    equipment_activity_uomctg_id = fields.Many2one('uom.category', 'Equipment Activity UoM Category',
                                                   related='equipment_activity_id.uom_id.category_id', readonly=True,
                                                   store=True
                                                   )
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure',
                             domain="[('category_id', '=', equipment_activity_uomctg_id)]")
    tracking_date = fields.Datetime('Tracking Date', default=fields.Datetime.now)
    tracking_value = fields.Integer('Tracking Value')
    tracking_eauom_value = fields.Integer('Tracking Value on Equipment Actv UoM',
                                          compute='_compute_tracking_eauom_value', store=True
                                          )

    @api.depends('equipment_activity_uomctg_id', 'uom_id', 'tracking_value')
    def _compute_tracking_eauom_value(self):
        for record in self:
            record.tracking_eauom_value = record.uom_id._compute_quantity(
                record.tracking_value,
                record.equipment_activity_id.uom_id
            )

    @api.onchange('equipment_activity_id')
    def _onchange_equipment_activity(self):
        if self.equipment_activity_id:
            self.uom_id = self.equipment_activity_id.uom_id

    @api.constrains('uom_id', 'equipment_activity_uomctg_id')
    def _check_uom_category(self):
        invalid_records = self.filtered(lambda r: r.uom_id.category_id != r.equipment_activity_uomctg_id)

        if invalid_records:
            raise ValidationError(_(
                "The following %s %s does not have the correct unit of measurement category"
            ) % (
                                      ',\n '.join(invalid_records.mapped('display_name')),
                                      _(self._description),
                                  ))


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    maintenance_guideline_ids = fields.Many2many('maintenance.guideline',
                                                 'maintenance_equipment_equipment_rel',
                                                 'mtn_guideline_id', 'mtn_equipment_id',
                                                 string='Guideline Of Maintenances')

    maintenance_actv_tracking_ids = fields.One2many('maintenance.equipment.activity.tracking',
                                                    'equipment_id', 'Activity Tracking')
    maintenance_actv_tracking_count = fields.Integer('Activity Tracking Count',
                                                     compute="_compute_maintenance_actv_tracking_count"
                                                     )
    equipment_activity_id = fields.Many2one('maintenance.equipment.activity', 'Equipment Activity',
                                            related="maintenance_guideline_ids.equipment_activity_id"
                                            )

    @api.depends('maintenance_actv_tracking_ids')
    def _compute_maintenance_actv_tracking_count(self):
        actv_tracking_data = self.env['maintenance.equipment.activity.tracking'].read_group([
            ('equipment_id', 'in', self.ids),
        ], ['equipment_id'], ['equipment_id'])

        result = dict((data['equipment_id'][0], data['equipment_id_count']) for data in actv_tracking_data)

        for equipment in self:
            equipment.maintenance_actv_tracking_count = result.get(equipment.id, 0)

    @api.model
    def _prepare_request_values(self, date):
        guideline = self.env['maintenance.guideline'].browse(self._context.get('default_maintenance_guideline_id'))

        values = {
            'name': _('Preventive Maintenance - %s') % self.name if not guideline.name else '%s - %s' % (
                guideline.name, self.name),
            'duration': guideline.maintenance_duration or self.maintenance_duration,
            'company_id': self.company_id.id or self.env.company.id,
            'user_id': self.technician_user_id.id,
            'category_id': self.category_id.id,
            'maintenance_type': 'preventive',
            'equipment_id': self.id,
            'schedule_date': date,
            'request_date': date,
        }

        if self.maintenance_team_id:
            values.update(maintenance_team_id=self.maintenance_team_id.id)
        if self.owner_user_id:
            values.update(owner_user_id=self.owner_user_id.id)

        return values

    # ----------------- FLOTA -----------------
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 domain=[('equipment_id', '=', False)],
                                 required=True,
                                 ondelete='cascade', index=True, check_company=True)

    odometer = fields.Float(string='Odometer', related='vehicle_id.odometer')
    odometer_unit = fields.Selection(
        selection=[('kilometers', 'km'),
                   ('miles', 'mi')
                   ], string='Odometer Unit', related='vehicle_id.odometer_unit')

    odometer_count = fields.Integer(related='vehicle_id.odometer_count', string='Odometer count')
    vehicle_type = fields.Selection(related='vehicle_id.vehicle_type')

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_odometer_action').read()[0]
        action['domain'] = [('vehicle_id', '=', self.vehicle_id.id)]
        context = dict(self._context, create=False, edit=False, delete=False)
        context.update({'default_vehicle_id': self.id})
        action['context'] = context
        return action

    @api.model
    def create(self, values):
        # Add code here
        res = super(MaintenanceEquipment, self).create(values)
        if 'maintenance_guideline_ids' in values:
            aux_ids = values.get('maintenance_guideline_ids', [])
            ids = []
            for aux in aux_ids:
                ids += aux[2]
            guideline_ids = res.env['maintenance.guideline'].browse(ids)
            for guideline in guideline_ids:
                if res not in guideline.equipment_ids:
                    self.env.context = dict(self.env.context)
                    self.env.context.update({'flag_update_from_equipment': True})
                    guideline.equipment_ids = [(4, res.id)]

        # conexión con flota
        if 'vehicle_id' in values:
            vehicle_id = self.vehicle_id.browse(values['vehicle_id'])
            vehicle_id.equipment_id = res.id
        return res

    def write(self, values):
        # Add code here
        vehicle_aux_id = self.vehicle_id
        res = super(MaintenanceEquipment, self).write(values)
        self.env.context = dict(self.env.context)

        flag_update_from_guideline = self._context.get('flag_update_from_guideline', False)
        if 'maintenance_guideline_ids' in values and not flag_update_from_guideline:
            aux_ids = values.get('maintenance_guideline_ids', [])
            ids = []
            for aux in aux_ids:
                ids += aux[2]
            guideline_ids = self.env['maintenance.guideline'].browse(ids)
            for guideline in guideline_ids:
                if self not in guideline.equipment_ids:
                    self.env.context.update({'flag_update_from_equipment': True})
                    guideline.equipment_ids = [(4, self.id)]
            guidelines_all = self.env['maintenance.guideline'].search([])
            equipment_guidelines = guidelines_all.filtered(lambda e: self in e.equipment_ids)
            if equipment_guidelines:
                guidelines_delete = list(set(equipment_guidelines) - set(guideline_ids))
                self.env.context.update({'flag_update_from_equipment': True})
                for g in guidelines_delete:
                    g.equipment_ids = [(3, self.id)]

        # conexión con flota
        if 'vehicle_id' in values:
            vehicle_id = self.vehicle_id.browse(values['vehicle_id'])
            vehicle_id.equipment_id = self.id
            if vehicle_aux_id:
                vehicle_aux_id.equipment_id = False
        return res

    flag_reload_maintenance_count = fields.Boolean(
        string='flag_reload_maintenance_count',
        compute='_compute_flag_reload_maintenance_count')

    @api.depends('maintenance_ids.stage_id.done')
    def _compute_flag_reload_maintenance_count(self):
        for rec in self:
            rec.sudo()._compute_maintenance_count()
            rec.sudo().flag_reload_maintenance_count = True

    # def _register_hook(self):
    #     """ Patch models to correct the that should trigger action rules based on creation,
    #         modification, deletion of records and form onchanges.
    #     """
    #
    #     def make__compute_next_maintenance():
    #         """ Instanciate the _compute_next_maintenance. """
    #
    #         @api.depends('effective_date', 'period', 'maintenance_ids.request_date', 'maintenance_ids.close_date')
    #         def _compute_next_maintenance(self):
    #             date_now = fields.Date.context_today(self)
    #             equipments = self.filtered(lambda x: any(mg.period > 0 or mg.value > 0
    #                                                      for mg in x.maintenance_guideline_ids))
    #
    #             for equipment in equipments:
    #                 next_maintenance_todo = self.env['maintenance.request'].search([
    #                     ('equipment_id', '=', equipment.id),
    #                     ('maintenance_type', '=', 'preventive'),
    #                     ('stage_id.done', '!=', True),
    #                     ('close_date', '=', False),
    #                 ], order="request_date asc", limit=1)
    #                 if next_maintenance_todo:
    #                     next_date = next_maintenance_todo.request_date
    #                     # If the new date still in the past, we set it for today
    #                     if next_date < date_now:
    #                         next_date = date_now
    #                 else:
    #                     next_date = False
    #                 equipment.next_action_date = next_date
    #
    #             (self - equipments).next_action_date = False
    #
    #         return _compute_next_maintenance
    #
    #     def make__create_new_request():
    #         def _create_new_request(self, date):
    #             self.ensure_one()
    #             self.env['maintenance.request'].create(self._prepare_request_values(date))
    #
    #         return _create_new_request
    #
    #     def make__cron_generate_requests():
    #         """ Instanciate the _compute_next_maintenance. """
    #
    #         @api.model
    #         def _cron_generate_requests(self):
    #             """
    #                 Generates maintenance request on the next_action_date or today if none exists
    #             """
    #             TrackingSudo = self.env['maintenance.equipment.activity.tracking'].sudo()
    #             today = fields.Date.context_today(self)
    #             tracking_value_delta = 3
    #
    #             for guideline in self.env['maintenance.guideline'].search(['|', ('period', '>', 0), ('value', '>', 0)]):
    #                 equipment = guideline.equipment_id
    #
    #                 next_requests = self.env['maintenance.request'].search([
    #                     ('request_date', '=', equipment.next_action_date),
    #                     ('maintenance_guideline_id', '=', guideline.id),
    #                     ('equipment_id', '=', equipment.id),
    #                     ('maintenance_type', '=', 'preventive'),
    #                     ('stage_id.done', '=', False),
    #                 ])
    #
    #                 if not next_requests:
    #                     tracking_data = TrackingSudo.read_group([
    #                         ('equipment_activity_id', '=', guideline.equipment_activity_id.id),
    #                         ('equipment_id', '=', equipment.id),
    #                     ], ['equipment_activity_id', 'tracking_eauom_value'], 'tracking_eauom_value')
    #                     if not tracking_data:
    #                         continue
    #
    #                     tracking_value = tracking_data[0]['tracking_eauom_value']
    #
    #                     if guideline.measurement == 'frequently':
    #                         tracking_limit_low = guideline.value - tracking_value_delta
    #                         tracking_limit_hight = tracking_value_delta
    #                         tracking_value %= guideline.period
    #                         if tracking_limit_hight < tracking_value < tracking_limit_low:
    #                             continue
    #                     else:
    #                         tracking_limit_hight = guideline.value + tracking_value_delta
    #                         tracking_limit_low = guideline.value - tracking_value_delta
    #                         if not tracking_limit_low <= tracking_value <= tracking_limit_hight:
    #                             continue
    #
    #                     equipment.with_context(default_maintenance_guideline_id=guideline.id)._create_new_request(today)
    #
    #         return _cron_generate_requests
    #
    #     bases = type(self).mro()
    #     bases.reverse()
    #     make_patched_methods = [(method_name[5:], method_patch)
    #                             for method_name, method_patch in locals().items()
    #                             if 'make_' in method_name]
    #
    #     for base in bases:
    #         if hasattr(base, '_name') and base._name == self._name:
    #             methods_2patch = [(method_name, method_patch)
    #                               for method_name, method_patch in make_patched_methods
    #                               if hasattr(base, method_name)]
    #
    #             for method_name, method_patch in methods_2patch:
    #                 base._patch_method(method_name, method_patch())
    #                 patched_method = getattr(base, method_name)
    #                 patched_method.origin_base = base
    #                 # mark the method as patched
    #                 make_patched_methods.remove((method_name, method_patch))
    #
    #         if not make_patched_methods:
    #             break
    #
    #     super(MaintenanceEquipment, self)._register_hook()
