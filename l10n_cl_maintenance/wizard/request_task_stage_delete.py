# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import ast


class RequestTaskStageDelete(models.TransientModel):
    _name = 'rt.stage.delete.wizard'
    _description = 'Request Stage Delete Wizard'

    request_ids = fields.Many2many('maintenance.request', string='Requests', ondelete='cascade')
    stage_ids = fields.Many2many('maintenance.request.task.stage', string='Stages To Delete', ondelete='cascade')
    tasks_count = fields.Integer('Number of tasks', compute='_compute_tasks_count')
    stages_active = fields.Boolean(compute='_compute_stages_active')

    @api.depends('request_ids')
    def _compute_tasks_count(self):
        for wizard in self:
            wizard.tasks_count = self.with_context(active_test=False).env['maintenance.request.task'].search_count(
                [('stage_id', 'in', wizard.stage_ids.ids)])

    @api.depends('stage_ids')
    def _compute_stages_active(self):
        for wizard in self:
            wizard.stages_active = all(wizard.stage_ids.mapped('active'))

    def action_archive(self):
        if len(self.request_ids) <= 1:
            return self.action_confirm()

        return {
            'name': _('Confirmation'),
            'view_mode': 'form',
            'res_model': 'rt.stage.delete.wizard',
            'views': [
                (self.env.ref('l10n_cl_maintenance.rt_stage_delete_wz_view_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_confirm(self):
        tasks = self.with_context(active_test=False).env['maintenance.request.task'].search(
            [('stage_id', 'in', self.stage_ids.ids)])
        tasks.write({'active': False})
        self.stage_ids.write({'active': False})
        return self._get_action()

    def action_unlink(self):
        self.stage_ids.unlink()
        return self._get_action()

    def _get_action(self):
        request_id = self.env.context.get('default_request_id')

        if request_id:
            action = self.env["ir.actions.actions"]._for_xml_id("l10n_cl_maintenance.maintenance_request_task_action")
            action['domain'] = [('request_id', '=', request_id)]
            action['context'] = str({
                'pivot_row_groupby': ['user_id'],
                'default_request_id': request_id,
            })
        elif self.env.context.get('stage_view'):
            action = self.env["ir.actions.actions"]._for_xml_id(
                "l10n_cl_maintenance.maintenance_request_task_stage_act_window")
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("l10n_cl_maintenance.maintenance_request_task_action")

        context = dict(ast.literal_eval(action.get('context')), active_test=True)
        action['context'] = context
        action['target'] = 'main'
        return action
