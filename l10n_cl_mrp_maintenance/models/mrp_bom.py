from odoo import models, fields


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    system_class_id = fields.Many2one(
        'maintenance.system.classification',
        domain=[('allocation_level', '=', True)],
        string='Component system', ondelete='restrict',
        required=True)
