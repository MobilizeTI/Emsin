from random import randint

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class HrSpecialty(models.Model):
    _name = 'hr.specialty.tag'
    _description = 'Hr Specialty Tag'

    def get_default_color_value(self):
        return randint(1, 15)

    name = fields.Char(string="Speciality", required=True)
    color_test = fields.Char(
        string="Color",
        help="Choose your color"
    )
    color = fields.Integer(
        string="Color Index (0-15)", default=lambda self: self.get_default_color_value()
    )
    equipment_ids = fields.Many2many(
        "guideline.activity",
        "guideline_activity_tag_rel",
        "specialty_tag_id",
        "activity_id",
        string="Activities",
    )

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The specialty name must be unique!'),
    ]
