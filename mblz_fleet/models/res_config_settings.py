# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    limit_odometer = fields.Integer(string='Limit odoometer', default=500)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('mblz_fleet.limit_odometer', self.limit_odometer)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        OBJ_CFG = self.env['ir.config_parameter'].sudo()
        limit_odometer = OBJ_CFG.get_param('mblz_fleet.limit_odometer')
        res.update(limit_odometer=limit_odometer)
        return res
