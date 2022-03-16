# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from datetime import timedelta


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    to_return = fields.Boolean('Para devolver')
    to_return_date = fields.Date('Fecha devolución')
    
    @api.onchange('product_id')
    def _onchange_product_return(self):
        if self.product_id and self.picking_type_id.is_requisition and self.product_id.to_return:
            self.to_return = True
            self.to_return_date = self.date + timedelta(days=self.product_id.to_return_days)
            
            
class StockMove(models.Model):
    _inherit = 'stock.move.line'
    
    picking_type_id = fields.Many2one('stock.picking.type', related='picking_id.picking_type_id')
    to_return = fields.Boolean('Para devolver', store=True, readonly=False, compute='_compute_returns')
    to_return_date = fields.Date('Fecha devolución', store=True, readonly=False, compute='_compute_returns')
    
    @api.depends('move_id', 'move_id.to_return', 'move_id.to_return_date')
    def _compute_returns(self):
        for rec in self:
            if rec.move_id.to_return_date:
                rec.to_return = rec.move_id.to_return
                rec.to_return_date = rec.move_id.to_return_date
            else:
                rec.to_return = rec.to_return or False
                rec.to_return_date = rec.to_return_date or False
    
    @api.onchange('product_id')
    def _onchange_product_return(self):
        if self.product_id and self.picking_type_id.is_requisition and self.product_id.to_return:
            self.to_return = True
            self.to_return_date = self.date + timedelta(days=self.product_id.to_return_days)