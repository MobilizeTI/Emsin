from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment',
                                   ondelete='cascade', index=True, check_company=True, copy=False)

    maintenance_count = fields.Integer(related='equipment_id.maintenance_count')

    assigned_equipment_id = fields.Boolean(
        string=' assigned_equipment_id',
        compute='_compute_assigned_equipment_id')

    def _compute_assigned_equipment_id(self):
        for record in self:
            if not record.equipment_id:
                equipment = record.env['maintenance.equipment'].sudo().search(
                    [('vehicle_id', '=', record.id), ('company_id', '=', record.env.company.id)], limit=1)
                if equipment:
                    record.equipment_id = equipment.id
            record.assigned_equipment_id = True

    def return_action_to_open(self):
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        opc_maintenance = self.env.context.get('opc_maintenance', False)
        if opc_maintenance:
            if xml_id:
                res = self.env['ir.actions.act_window']._for_xml_id('maintenance.%s' % xml_id)
                res.update(
                    context=dict(self.env.context, default_equipment_id=self.equipment_id.id, group_by=False),
                    domain=[('equipment_id', '=', self.equipment_id.id)]
                )
                return res
            return False
        else:
            return super(FleetVehicle, self).return_action_to_open()
