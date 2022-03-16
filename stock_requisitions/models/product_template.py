# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    to_return = fields.Boolean('Para devolver', help='Marque el producto para que se auto-genere una devolución del mismo en otro momento')
    to_return_days = fields.Integer('Días para devolver', default=1, help='Indique la cantidad de días para devolver el producto, se generará un picking para la cantidad de días después')