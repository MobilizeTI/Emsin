from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    invoice_render_method = fields.Selection(
        selection=[
            ('standard', 'Estándar'),
            ('line_per_sale', 'Por Pedido'),
            ('one_line', 'Un sólo concepto')
            ],
        string='Método de Impresión de Facturación')
    
    def _compare_display_type(self, display_type):
        if display_type == 'line_section':
            return 0
        else:
            return 1
    
    def _sort_lines(self):
        sequence = 1
        if self.invoice_render_method == 'line_per_sale':
            sales_orders = self.line_ids.mapped('sale_order_id')
            for sale in sales_orders:
                sorted_lines = self.line_ids.filtered(lambda aml: aml.sale_order_id.id == sale.id).sorted(key=lambda l: self._compare_display_type(l.display_type))
                for line in sorted_lines:
                    line.sequence = sequence
                    sequence += 1
        elif self.invoice_render_method == 'one_line':
            sorted_lines = self.line_ids.sorted(key=lambda l: self._compare_display_type(l.display_type))
            for line in sorted_lines:
                line.sequence = sequence
                sequence += 1
    
    def get_printeable_lines(self):
        if self.invoice_render_method in ['one_line', 'line_per_sale']:
            return self.line_ids.filtered(lambda aml: aml.display_type == 'line_section')
        else:
            return self.invoice_line_ids
    
    def get_sale_group_untaxed(self, line):
        sale_order_id = self.env['sale.order'].browse(int(line.sale_order_id))
        lines = self.line_ids.filtered(lambda l: l.sale_order_id == sale_order_id)
        return sum(lines.mapped('price_subtotal'))

    def currency_format(self, val, precision='Product Price'):
        code = self._context.get('lang')
        lang = self.env['res.lang'].search([('code', '=', code)])
        string_digits = '%.{}f'.format(0)
        res = lang.format(string_digits, val , grouping=True, monetary=True)
        if self.currency_id.symbol:
            if self.currency_id.position == 'after':
                res = '%s %s' % (res, self.currency_id.symbol)
            elif self.currency_id.position == 'before':
                res = '%s %s' % (self.currency_id.symbol, res)
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    sale_order_id = fields.Many2one('sale.order')
    
    
    