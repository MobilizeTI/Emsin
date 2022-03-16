# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SelectMultipleProduct(models.Model):
    _name = 'select.multiple.product'
    _description = 'Add multiple products'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)
    products_multiple_ids = fields.Many2many('product.product',
                                             'wz_select_multiple_product_rel',
                                             'wz_select_id', 'product_id', check_company=True,
                                             string='Products')

    def action_add(self):
        active_id = self._context.get('active_id')
        if active_id and self.products_multiple_ids:
            bom_id = self.env['mrp.bom'].browse(active_id)
            bom_line_ids = []

            products_ids = bom_id.bom_line_ids.mapped('product_id')
            for product in self.products_multiple_ids:
                if product not in products_ids:
                    # Si no existe se añade
                    bom_line_ids.append((0, 0, dict(bom_id=active_id,
                                                    product_id=product.id,
                                                    )))
                # else:
                #     # Se actualiza la cantidad en +1
                #     lines = bom_id.bom_line_ids.filtered(lambda c: c.product_id == product)
                #     if lines:
                #         for item in lines:
                #             value = item.product_qty + 1
                #             item.product_qty = value
            bom_id.bom_line_ids = bom_line_ids


# class SelectMultipleProductLine(models.Model):
#     _name = 'select.multiple.product.line'
#     _description = 'Select Multiple Product Line'
#     _rec_name = "product_id"
#     _check_company_auto = True
#
#     def _get_default_product_uom_id(self):
#         return self.env['uom.uom'].search([], limit=1, order='id').id
#
#     company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)
#     product_id = fields.Many2one('product.product', 'Component', required=True, check_company=True)
#     product_qty = fields.Float(
#         'Quantity', default=1.0,
#         digits='Product Unit of Measure', required=True)
#
#     product_uom_id = fields.Many2one(
#         'uom.uom', 'Product Unit of Measure',
#         default=_get_default_product_uom_id,
#         required=True,
#         help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control",
#         domain="[('category_id', '=', product_uom_category_id)]")
#     product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
