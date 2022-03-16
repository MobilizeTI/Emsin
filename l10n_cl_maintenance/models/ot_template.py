# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta


class OTTemplate(models.Model):
    _name = "ot.template"
    _description = "OT template for scheduler"
    _rec_name = 'name_header'

    name_header = fields.Char(string='Name header', required=True)

    # guideline_id = fields.Many2one('maintenance.guideline',
    #                                string='Guideline', required=True,
    #                                ondelete='cascade', index=True,
    #                                copy=False)

    type_ot = fields.Many2one('maintenance.request.type',
                              domain=[('maintenance_type', '=', 'preventive')],
                              string='Type OT', required=True)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)

    @api.onchange('user_id')
    def onchange_method(self):
        self.employee_id = self.user_id.employee_id.id

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)

    def name_get(self):
        result = []
        for rec in self:
            name = f'Plantilla: {rec.name_header}'
            result.append((rec.id, name))
        return result
