# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# Nivel de falla
class HelpdeskFailureLevel(models.Model):
    _name = 'helpdesk.failure.level'
    _description = 'Failure level'

    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True, copy=False)
    time_response = fields.Float(string='Response time (minutes)', required=True)
    time_solution = fields.Float(string='Solution Time (hours)', required=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
        except ValueError:
            default['name'] = self.name
        return super(HelpdeskFailureLevel, self).copy(default)
