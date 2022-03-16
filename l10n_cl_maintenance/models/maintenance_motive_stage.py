# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models

from odoo.addons.base.models import ir_ui_view


class MaintenanceMotiveStage(models.Model):
    _name = "maintenance.motive.stage"
    _description = 'Maintenance motive stage'

    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description', required=False)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The motive name must be unique!'),
    ]



