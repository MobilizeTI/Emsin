# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models, _
from pprint import pprint
from lxml import etree

from odoo.addons.base.models import ir_ui_view
from odoo.exceptions import ValidationError


class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    request_motive = fields.Boolean("Request motive")


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    stage_id = fields.Many2one("maintenance.stage", readonly=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            doc = etree.XML(res["arch"])
            stages = self.env["maintenance.stage"].search([], order="sequence desc")
            header = doc.xpath("//form/header")[0]
            for stage in stages:
                node = stage._get_stage_node()
                self._setup_modifiers(node)
                header.insert(0, node)
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    def set_maintenance_stage(self):
        if not self.env.context.get("next_stage_id"):
            return {}
        next_stage_id = self.env.context.get("next_stage_id")

        stage_dif = self.env['maintenance.stage'].browse(next_stage_id)
        if stage_dif:
            xml_groups_ids = stage_dif.get_xml_groups_ids()
            flag_group = False
            for xml_id in xml_groups_ids:
                if self.env.user.has_group(xml_id):
                    flag_group = True
            if not flag_group:
                raise ValidationError(_(f'No tiene permiso para cambiar de estado a {stage_dif.name}'))

        if stage_dif.request_motive:
            return self.open_motive_wizard(next_stage_id)
        else:
            return self._set_maintenance_stage(next_stage_id)

    def _set_maintenance_stage(self, next_stage_id):
        self.sudo().write({"stage_id": next_stage_id})

    @api.model
    def _setup_modifiers(self, node):
        modifiers = {}
        ir_ui_view.transfer_node_to_modifiers(node, modifiers)
        ir_ui_view.transfer_modifiers_to_node(modifiers, node)

    def open_motive_wizard(self, next_stage_id=6):
        view = self.env.ref('maintenance_request_stage_transition.stage_motive_wizard_view_form', False)
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['default_stage_id'] = next_stage_id
        context['default_request_id'] = self.id
        return {
            'name': _('Confirm Motive'),
            'type': 'ir.actions.act_window',
            'res_model': 'stage.motive.wizard',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }

    flag_stage_request_motive = fields.Boolean(related='stage_id.request_motive', string='Request motive change stage')

    motive_log_ids = fields.One2many('maintenance.motive.log', 'request_id',
                                     'Detail motives', copy=True,
                                     auto_join=True)

    is_deferred = fields.Boolean(string='Is deferred', required=False)
    is_waiting = fields.Boolean(string='Is waiting', required=False)

    last_motive = fields.Many2one('maintenance.motive.stage', string='Motive',
                                  compute='_compute_last_motive_comment')
    last_comment = fields.Text('Comment', compute='_compute_last_motive_comment')
    flag_with_motive = fields.Boolean(
        string='With motives',
        compute='_compute_flag_with_motive', store=True)

    @api.depends('motive_log_ids')
    def _compute_flag_with_motive(self):
        for request in self:
            request.sudo().flag_with_motive = request.motive_log_ids.exists()

    @api.depends('motive_log_ids')
    def _compute_last_motive_comment(self):
        for request in self:
            if request.motive_log_ids:
                request.sudo().flag_with_motive = True
                record = request.motive_log_ids.sorted(lambda l: l.date, reverse=True)[0]
                request.sudo().last_motive = record.motive_id.id
                request.sudo().last_comment = record.comment
            else:
                request.sudo().flag_with_motive = False
                request.sudo().last_motive = False
                request.sudo().last_comment = False

    @api.model
    def update_is_deferred_waiting(self):
        requests = self.search([])
        for r in requests:
            if r.motive_log_ids:
                deferred = r.motive_log_ids.filtered(lambda l: l.stage_name == 'Diferido')
                if deferred:
                    r.is_deferred = True

                waiting = r.motive_log_ids.filtered(lambda l: l.stage_name == 'En espera')
                if waiting:
                    r.is_waiting = True


class MaintenanceMotiveLog(models.Model):
    _name = 'maintenance.motive.log'
    _description = "Log motives"

    date = fields.Datetime('Date time', default=lambda self: fields.datetime.now())
    request_id = fields.Many2one('maintenance.request',
                                 string='Request',
                                 required=True,
                                 ondelete='cascade',
                                 index=True, copy=False
                                 )
    motive_id = fields.Many2one('maintenance.motive.stage', string='Motive',
                                required=True)
    comment = fields.Text('Comment:', required=False)
    stage_name = fields.Char(string='Stage')
