# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    is_requisition = fields.Boolean('Requisiciones', related='picking_type_id.is_requisition')
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        
        dates = list(set(self.move_line_ids_without_package.mapped('to_return_date')))        
        
        if any(self.move_line_ids_without_package.mapped('to_return')):
            SP = self.env['stock.picking']
            
            for d in dates:
                picking = SP.with_user(SUPERUSER_ID).create({
                    'partner_id': self.partner_id.id,
                    'picking_type_id': self.picking_type_id.return_picking_type_id.id,
                    'user_id': self.user_id.id,
                    'origin': self.name,
                    'location_id': self.picking_type_id.default_location_dest_id.id or self.env.ref('stock.stock_location_customers').id,
                    'location_dest_id': self.picking_type_id.return_picking_type_id.default_location_dest_id.id,
                    'company_id': self.company_id.id
                })
                
                for item_line in self.move_line_ids_without_package.filtered(lambda self: self.to_return_date == d):
                    if item_line.qty_done:
                        picking.write({
                            'move_ids_without_package': [(0, 0, {
                                'name': item_line.product_id.display_name,
                                'product_id': item_line.product_id.id,
                                'product_uom_qty': item_line.qty_done,
                                'product_uom': item_line.product_uom_id.id,
                                'location_id': self.picking_type_id.default_location_dest_id.id or self.env.ref('stock.stock_location_customers').id,
                                'location_dest_id': self.picking_type_id.return_picking_type_id.default_location_dest_id.id,
                            })]
                        })
                        
                picking.write({'scheduled_date': d})
        
        return res