from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class MaintenanceComponent(models.Model):
    _name = 'maintenance.system.classification'
    _description = 'Maintenance System Classification'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean('Active', default=True)
    allocation_level = fields.Boolean(string='Allocation level', required=False)

    code = fields.Char(string='Code', required=True, copy=False)
    name = fields.Char(string='Name', required=True, copy=False)

    parent_ids = fields.Many2many('maintenance.system', string='Parents')

    description = fields.Html(string='Description', required=False)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})

        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
            default.setdefault('code', _("%s (copy)") % (self.code or ''))
        except ValueError:
            default['code'] = _("%s (copy)") % (self.code or '')
            default['name'] = self.name
        return super(MaintenanceComponent, self).copy(default)

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The system classification name must be unique!'),
        ('unique_code', 'unique (code)', 'The system classification code must be unique!'),
    ]
