# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo import _, fields, models, api


class MaintenanceStage(models.Model):
    _inherit = "maintenance.stage"

    next_stage_ids = fields.Many2many(
        "maintenance.stage",
        string="Next stages",
        relation="maintenance_stage_next_stage",
        column1="stage_id",
        column2="next_stage_id",
    )

    previous_stage_ids = fields.Many2many(
        "maintenance.stage",
        string="Previous stages",
        relation="maintenance_stage_next_stage",
        column1="next_stage_id",
        column2="stage_id",
    )

    group_ids = fields.Many2many('res.groups', string='Groups',
                                 relation="maintenance_stage_groups",
                                 column1="next_stage_user_id",
                                 column2="user_id")

    group_profile_ids = fields.Many2many('res.groups', string='Groups profile',
                                         relation="maintenance_stage_groups",
                                         column1="user_id",
                                         column2="next_stage_user_id", compute='_compute_group_ids')

    def _compute_group_ids(self):
        group_profiles = self.env['res.groups'].sudo().search(
            [('category_id', '=', self.env.ref('l10n_cl_maintenance.category_group_perfil_mueve').id)])
        for rec in self:
            rec.group_profile_ids = [(6, 0, group_profiles.ids)]

    button_class = fields.Selection(
        [
            ("primary", "Primary"),
            ("info", "Info"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        help="For default, the system uses primary",
    )

    def _get_stage_node_attrs(self):
        return {"invisible": [("stage_id", "not in", self.previous_stage_ids.ids)]}

    def _get_stage_node_name(self):
        return _("To %s") % self.name

    def get_xml_groups_ids(self, opc='a'):
        group_id_xml = []
        for index, group in enumerate(self.group_ids):
            res = group.get_external_id()
            if res.get(group.id):
                group_id_xml.append(res.get(group.id))
        if opc == 'b':
            return ','.join(group_id_xml) if group_id_xml else False
        else:
            return group_id_xml

    def _get_stage_node(self):
        attrib = {
            "name": "set_maintenance_stage",
            "id": str(self.id),
            "type": "object",
            "class": "btn-%s" % (self.button_class or "primary"),
            "context": json.dumps({"next_stage_id": self.id}),
            "attrs": json.dumps(self._get_stage_node_attrs()),
            "string": self._get_stage_node_name(),
        }
        # groups = self.get_xml_groups_ids(opc='b')
        # if groups:
        #     attrib['groups'] = groups
        return etree.Element("button", attrib=attrib)
