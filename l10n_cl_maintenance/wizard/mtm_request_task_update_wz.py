# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MTMRequestTaskWZ(models.TransientModel):
    _name = 'mtm.request.task.wz'
    _description = 'Add multiple task employee'

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True)

    task_ids = fields.Many2many('maintenance.request.task', string='Tasks')

    count_task_ids = fields.Integer(
        string='Quantity of tasks',
        compute='_compute_count_task_ids')

    @api.depends('task_ids')
    def _compute_count_task_ids(self):
        for rec in self:
            rec.count_task_ids = len(rec.task_ids) if rec.task_ids else 0

    specialty_tag_ids = fields.Many2many("hr.specialty.tag", string="Specialities",
                                         compute='_compute_specialty_tag_ids')

    @api.depends('task_ids')
    def _compute_specialty_tag_ids(self):
        for rec in self:
            if rec.task_ids:
                specialty_tag_ids = []
                for task in rec.task_ids:
                    specialty_tag_ids += task.activity_speciality_ids.ids
                rec.specialty_tag_ids = [(6, 0, list(set(specialty_tag_ids)))]
            else:
                rec.specialty_tag_ids = [(6, 0, [])]

    def btn_confirm(self):
        self.ensure_one()
        for task in self.task_ids:
            task.write({
                'employee_id': self.employee_id.id
            })
