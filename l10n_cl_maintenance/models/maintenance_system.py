from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class MaintenanceSystem(models.Model):
    _name = 'maintenance.system'
    _description = 'Maintenance System'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _parent_order = "name"
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean('Active', default=True)
    allocation_level = fields.Boolean(string='Allocation level', required=False)

    name = fields.Char(string='Name', required=True, copy=False)

    display_name = fields.Char(compute="_compute_display_name")

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('maintenance.system',
                                'Parent system',
                                index=True,
                                ondelete='cascade')

    parent_left = fields.Integer("Left Parent", index=1)
    parent_right = fields.Integer("Right Parent", index=1)
    child_count = fields.Integer(
        compute="_compute_child_count", string="Number of child equipments"
    )

    parent_path = fields.Char(index=True, string='parent_path')
    # parent_path_ids = fields.Char(compute='_compute_parent_path')
    child_ids = fields.One2many('maintenance.system', 'parent_id', 'Child System Classification')

    @api.depends("child_ids")
    def _compute_child_count(self):
        for equipment in self:
            equipment.child_count = len(equipment.child_ids)

    def _compute_display_name(self):
        for equipment in self:
            equipment.display_name = equipment.complete_name

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for system in self:
            if system.parent_id:
                system.complete_name = '%s / %s' % (system.parent_id.complete_name, system.name)
            else:
                system.complete_name = system.name

    def preview_child_list(self):
        return {
            "name": "Child system classification of %s" % self.name,
            "type": "ir.actions.act_window",
            "res_model": "maintenance.system",
            "res_id": self.id,
            "view_mode": "list,form",
            "context": {
                **self.env.context,
                "default_parent_id": self.id,
                "parent_id_editable": False,
            },
            "domain": [("id", "in", self.child_ids.ids)],
        }

    # @api.depends('parent_id')
    # def _compute_parent_path(self):
    #     for system in self:
    #         if system.parent_id:
    #             x = '/%s/%s/' % (system.parent_id.parent_path_ids, system.id)
    #             x = x.replace('//', '/')
    #             system.parent_path_ids = x
    #         else:
    #             system.parent_path_ids = f'/{system.id}/'

    @api.constrains('parent_id')
    def _check_guideline_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive System.'))
        return True

    description = fields.Html(string='Description', required=False)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})

        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
        except ValueError:
            default['name'] = self.name
        return super(MaintenanceSystem, self).copy(default)

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The system classification name must be unique!'),
    ]
