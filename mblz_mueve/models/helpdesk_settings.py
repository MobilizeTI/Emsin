from odoo import models, fields, api, _
from ast import literal_eval


class HelpdeskSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_portal = fields.Char(string='Default email portal')

    def set_values(self):
        res = super(HelpdeskSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('mblz_mueve.email_portal', self.email_portal)
        # print("email_portal", self.email_portal)
        return res

    @api.model
    def get_values(self):
        res = super(HelpdeskSettings, self).get_values()
        OBJ_CFG = self.env['ir.config_parameter'].sudo()
        email_portal = OBJ_CFG.get_param('mblz_mueve.email_portal')
        res.update(email_portal=email_portal)
        return res
