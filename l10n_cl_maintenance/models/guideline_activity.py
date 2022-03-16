from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError


class MaintenanceGuidelineActivity(models.Model):
    _name = 'guideline.activity'
    _description = 'Guideline Activity'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _parent_order = "name,code"

    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean('Active', default=True)

    code = fields.Char(string='Code', required=True, copy=False)
    name = fields.Char(string='Name', required=True, copy=False)
    system_class_id = fields.Many2one(
        'maintenance.system.classification',
        domain=[('allocation_level', '=', True)],
        string='Component',
        required=False)

    display_name = fields.Char(compute="_compute_display_name")

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('guideline.activity',
                                'Parent Activity',
                                index=True,
                                ondelete='cascade')

    parent_left = fields.Integer("Left Parent", index=1)
    parent_right = fields.Integer("Right Parent", index=1)
    child_count = fields.Integer(
        compute="_compute_child_count", string="Number of child equipments"
    )

    parent_path = fields.Char(index=True, string='parent_path')
    # parent_path_ids = fields.Char(compute='_compute_parent_path')
    child_ids = fields.One2many('guideline.activity', 'parent_id', 'Child activities')
    duration = fields.Float(help="Duration in hours.")

    @api.depends("child_ids")
    def _compute_child_count(self):
        for equipment in self:
            equipment.child_count = len(equipment.child_ids)

    def _compute_display_name(self):
        for equipment in self:
            equipment.display_name = equipment.complete_name

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for guideline in self:
            if guideline.parent_id:
                guideline.complete_name = '%s / %s' % (guideline.parent_id.complete_name, guideline.name)
            else:
                guideline.complete_name = guideline.name

    def preview_child_list(self):
        return {
            "name": "Child activity of %s" % self.name,
            "type": "ir.actions.act_window",
            "res_model": "guideline.activity",
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
    #     for guideline in self:
    #         if guideline.parent_id:
    #             x = '/%s/%s/' % (guideline.parent_id.parent_path_ids, guideline.id)
    #             x = x.replace('//', '/')
    #             guideline.parent_path_ids = x
    #         else:
    #             guideline.parent_path_ids = f'/{guideline.id}/'

    @api.constrains('parent_id')
    def _check_guideline_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive activities.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    att_documents = fields.Many2many('ir.attachment', string='Documents', required=False)
    description = fields.Html(string='Description', required=False)

    url_ids = fields.One2many('activity.url', 'activity_id', 'Urls', copy=True, auto_join=True)
    url_video = fields.Char(string='Url video', compute='_compute_url_video')

    @api.depends('url_ids')
    def _compute_url_video(self):
        for rec in self:
            if rec.url_ids and len(rec.url_ids) > 0:
                rec.url_video = rec.url_ids[0].name
            else:
                rec.url_video = None

    def action_open_url_video(self):
        self.ensure_one()
        if self.url_video:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url_video,
                'target': 'new',
            }
        else:
            raise Warning(_(f'the activity does not have an link assigned video'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
            default.setdefault('code', _("%s (copy)") % (self.code or ''))
        except ValueError:
            default['code'] = _("%s (copy)") % (self.code or '')
            default['name'] = self.name
        return super(MaintenanceGuidelineActivity, self).copy(default)

    specialty_tag_ids = fields.Many2many(
        "hr.specialty.tag",
        "guideline_activity_tag_rel",
        "activity_id",
        "specialty_tag_id",
        string="Specialities")

    # @api.constrains('name')
    # def _check_capacity(self):
    #     if any('/' in act.name for act in self):
    #         raise UserError(_('No debe exístir el caracter "/" en el nombre de la actividad.'))

    def name_get(self):
        # if self.env.context.get('not_show_name', False):
        return [(record.id, f'[{record.code}] {record.name}') for record in self]
        # return super(MaintenanceGuidelineActivity, self).name_get()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            activity_ids = self._search(['|', ('name', operator, name),
                                         ('code', operator, name)] + args,
                                        limit=limit, access_rights_uid=name_get_uid)
        else:
            activity_ids = self._search([])
        return activity_ids

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The activity name must be unique!'),
        ('unique_code', 'unique (code)', 'The activity code must be unique!'),
    ]


class ActivityUrl(models.Model):
    _name = 'activity.url'
    _description = 'activity urls'

    activity_id = fields.Many2one('guideline.activity', string='Activity', required=True, ondelete='cascade',
                                  index=True, copy=False)
    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description', required=False)
