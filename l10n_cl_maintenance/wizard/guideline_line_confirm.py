from odoo import fields, models, api


class GuidelineLineConfirm(models.TransientModel):
    _name = 'guideline.line.confirm'
    _description = 'Delete line guideline confirm'

    guideline_id = fields.Many2one('maintenance.guideline',
                                   string='Guideline',
                                   required=True)
    line_guideline = fields.Many2one('maintenance.guideline.activity',
                                     string='Guideline line',
                                     required=True)

    text_message = fields.Char(string='Text message', required=False)

    lines_dependent = fields.Many2many(
        'maintenance.guideline.activity',
        string='Lines_dependent', compute='_compute_lines_dependent')

    @api.depends('line_guideline')
    def _compute_lines_dependent(self):
        for rec in self:
            lines = rec._get_lines_dependent()
            rec.lines_dependent = [(6, 0, lines)]

    def _get_lines_dependent(self):
        lines_dependent = self.line_guideline.guideline_id.activities_ids
        my_id = str(self.line_guideline.activity_id.id)
        to_delete = lines_dependent.filtered(
            lambda i: my_id in i.activity_id.parent_path.split('/') and i.id != self.line_guideline.id).ids
        return to_delete

    def btn_confirm(self):
        self.lines_dependent.unlink()
        line_guideline = self.guideline_id.activities_ids.filtered(lambda l: l.id == self.line_guideline.id)
        line_guideline.unlink()
