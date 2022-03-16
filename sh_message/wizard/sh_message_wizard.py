# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _


class sh_message_wizard(models.TransientModel):
    _name = "sh.message.wizard"
    _description = "Message wizard to display warnings, alert ,success messages"

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)
    file = fields.Binary(string="Resultado: ")
    has_file = fields.Boolean(string='Tiene archivo')
    name_file = fields.Char(string='Name_file', required=False)
    result_ok = fields.Boolean(string='Result_ok', required=False)

    @api.depends('file')
    def _compute_has_file(self):
        for line in self:
            line.has_file = True if line.file else False
