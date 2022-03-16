# -*- coding: utf-8 -*-
from pprint import pprint

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    flag_crete_tkt_portal = fields.Boolean(
        string='Create tkt portal',
        required=False)
