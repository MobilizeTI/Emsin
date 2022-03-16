# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    
    is_requisition = fields.Boolean('Es para requisiciones')
    
    @api.onchange('code')
    def _onchange_code_requisition(self):
        if self.code != 'outgoing':
            self.is_requisition = False