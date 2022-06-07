from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import groupby

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def create_emsin_invoices(self):
        """"""
        view_id = self.env.ref('mblz_emsin.wizard_create_emsin_invoices').id
        return {'type': 'ir.actions.act_window',
                'name': _('Crear Facturas'),
                'res_model': 'wizard.create.invoices.emsin',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'active_ids': self.ids
                        },
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'sale_order_id': self.order_id.id
            
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    @api.model
    def _get_sale_orders(self):
        ids = self._context.get('active_ids', [])
        if ids:
            return self.env['sale.order'].sudo().search([('id', 'in', ids)]).ids
        else:
            return False
    
    @api.model
    def _get_one_line_concept(self):
        return "Factura Correspondiente a las Ordernes %s".replace('[', '').replace(']', '') % (self.sale_order_ids.mapped('name'))
    
    sale_order_ids = fields.Many2many('sale.order', string='Pedidos', default=_get_sale_orders)
    invoice_method = fields.Selection(
        selection=[
            ('standard', 'Estándar'),
            ('line_per_sale', 'Por Pedido'),
            ('one_line', 'Un sólo concepto')
            ],
        string='Método de Facturación', default='standard')
    one_line_concept = fields.Char('Concepto')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.onchange('invoice_method')
    def onchange_invoice_method(self):
        if self.invoice_method == 'one_line':
            raw_concept = "Factura Correspondiente a las Ordenes %s" % (self.sale_order_ids.mapped('name'))
            self.one_line_concept = raw_concept.replace('[', '').replace(']', '').replace("'", '')
    
    def create_invoices(self):
        if self.invoice_method == 'standard':
            return super(SaleAdvancePaymentInv, self).create_invoices()
        else:
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            if self.advance_payment_method == 'delivered':
                invoice_id = sale_orders._create_invoices(final=self.deduct_down_payments)
            else:
                # Create deposit product if necessary
                if not self.product_id:
                    vals = self._prepare_deposit_product()
                    self.product_id = self.env['product.product'].create(vals)
                    self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
                sale_line_obj = self.env['sale.order.line']
                for order in sale_orders:
                    amount, name = self._get_advance_details(order)
                    if self.product_id.invoice_policy != 'order':
                        raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                    if self.product_id.type != 'service':
                        raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                    taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                    tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                    analytic_tag_ids = []
                    for line in order.order_line:
                        analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                    so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                    so_line = sale_line_obj.create(so_line_values)
                    invoice_id = self._create_invoice(order, so_line, amount)
            if invoice_id:
                if self.invoice_method == 'one_line':
                    invoice_id.update({
                        'invoice_line_ids' : [(0, 0, {
                            'name': self.one_line_concept,
                            'quantity': 1.0,
                            'display_type': 'line_section',
                            'sequence': 1
                            })],
                        'invoice_render_method': 'one_line',
                        
                    })
                elif self.invoice_method == 'line_per_sale':
                    invoice_id.update({
                        'invoice_line_ids' : [(0, 0, {
                            'name': so.name,
                            'quantity': 1.0,
                            'sale_order_id': so.id,
                            'display_type': 'line_section',
                            }) for so in self.sale_order_ids],
                        'invoice_render_method': 'line_per_sale',
                        
                    })
                invoice_id._sort_lines()
                    
            if self._context.get('open_invoices', False):
                return sale_orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}
                        
    
    