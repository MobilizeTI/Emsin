# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SelectAllActivities(models.TransientModel):
    _name = 'select.all.activities'
    _description = 'Add multiple activities'

    guideline_id = fields.Many2one('maintenance.guideline',
                                   string='Guideline',
                                   check_company=True)

    activities_multiple_ids = fields.Many2many('guideline.activity',
                                               'wz_select_all_activity_rel',
                                               'wz_select_id', 'gd_activity_id',
                                               string='Activities')

    def action_add(self):
        active_id = self._context.get('active_id')
        if active_id and self.activities_multiple_ids:
            guideline_id = self.env['maintenance.guideline'].browse(active_id)
            add_ids = []
            activity_ids = guideline_id.activities_ids.mapped('activity_id')
            for activity in self.activities_multiple_ids:
                if activity not in activity_ids:
                    add_ids.append((0, 0, dict(guideline_id=active_id, activity_id=activity.id)))
            guideline_id.activities_ids = add_ids