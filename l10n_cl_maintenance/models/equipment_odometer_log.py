# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta


class EquipmentOdometerLog(models.Model):
    _name = "equipment.odometer.log"
    _description = "Equipment Odometer Log"

    date_log = fields.Date(string='Date', required=True, readonly=False,
                           default=lambda self: fields.datetime.now().date())
    guideline_id = fields.Many2one('maintenance.guideline',
                                   string='Guideline', required=True,
                                   ondelete='cascade', index=True,
                                   copy=False)
    type_auto_planning = fields.Selection(related='guideline_id.type_auto_planning')

    type_odometer = fields.Selection(
        string='Type',
        selection=[('latest', 'Start'),
                   ('next', 'Next'), ],
        default='latest',
        help="Latest: About the last recorded odometer in history\n"
             "Next: Proximate value for the creation of a TO"
    )

    @api.onchange('guideline_id')
    def onchange_guideline_id(self):
        if self.guideline_id.type_auto_planning == 'accumulated':
            self.type_odometer = 'next'
            self.next_odometer = self.guideline_id.percentage_value
        else:
            self.type_odometer = 'latest'

    equipment_id = fields.Many2one('maintenance.equipment',
                                   domain=[('vehicle_id', '!=', False), ('active', '=', True)],
                                   string='Equipment', required=True,
                                   ondelete='cascade', index=True,
                                   copy=False)
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle', related='equipment_id.vehicle_id')
    odometer = fields.Float(string='Actual odometer', related='vehicle_id.odometer')
    last_odometer = fields.Float(string='Last maintenance odometer', required=True)
    next_odometer = fields.Float(string='Odometer next maintenance')

    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
    ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)

    flag_process = fields.Boolean()

    @api.model
    def get_last_log(self, equipment_id, guideline_id):
        log = self.search([('equipment_id', '=', equipment_id), ('guideline_id', '=', guideline_id)], limit=1)
        if log:
            return log
        else:
            return False

    @api.model
    def is_log_date(self, equipment_id, guideline_id):
        log = self.search([('equipment_id', '=', equipment_id),
                           ('guideline_id', '=', guideline_id),
                           ], limit=1)
        res = {'log': log}
        if log:
            res.update({'ok': True})
            return res
        else:
            res.update({'ok': False})
            return res
