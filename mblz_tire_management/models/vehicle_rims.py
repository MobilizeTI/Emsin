# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VehicleRims(models.Model):
    _name = 'vehicle.rims'
    _description = 'Vehicle rims'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company.id)

    name = fields.Char(string='Model', required=True, copy=False)

    # FECHA (de registro)
    date_rec = fields.Date(string='Date', default=lambda self: fields.Date.today())
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 required=True, ondelete='restrict', index=True, check_company=True)

    # PPU (Placa patente única)
    license_plate = fields.Char(string='License plate', related='vehicle_id.license_plate')

    # POS (Posición de la llanta)
    rim_position = fields.Selection(
        string=' Rim position',
        selection=[('1', '1'),
                   ('2', '2'),
                   ('3', '3'),
                   ('4', '4'),
                   ('5', '5'),
                   ('6', '6')],
        required=False, )

    # NUMERO DE FUEGO (Numero interno impreso en la llanta)
    fire_number = fields.Char(string='Fire Number')

    product_id = fields.Many2one('product.product', string='Product',
                                 required=True, ondelete='cascade', index=True, check_company=True)
    # MARCA (Marca de la llanta)
    brand_id = fields.Many2one('product.brand', string='Brand', related='product_id.brand_id')

    # MODELO DEL NEUMATICO
    model_prod = fields.Char(string='Model', related='product_id.model_prod')
    # SKU
    default_code = fields.Char(string='SKU', related='product_id.default_code')
    # MARCA DE LA BANDA
    brand_band_id = fields.Many2one('product.brand', string='Brand band')

    # MODELO DE LA BANDA
    model_band = fields.Char(string='Model band')

    cycle = fields.Integer(string='Cycle', required=False)

    # MM (Milímetros de profundidad del labrado)
    mm_rim = fields.Integer(string='MM', required=False)

    # DEPOSITO (Ubicación de unidad de negocio)
    location_id = fields.Many2one(
        'stock.location', 'LOCATION',
        index=True, ondelete='cascade',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
        help="The parent location that includes this location. Example : The 'Dispatch Zone' is the 'Gate 1' parent location.")
