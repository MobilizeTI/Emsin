# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskSupportActivity(models.Model):
    _name = 'helpdesk.support.activity'
    _description = 'helpdesk.support.activity'

    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(string='Name', required=True, copy=False)
    description = fields.Text(required=False)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
        except ValueError:
            default['name'] = self.name
        return super(HelpdeskSupportActivity, self).copy(default)

    # line_ids = fields.One2many('helpdesk.support.activity.line', 'activity_id',
    #                            'Detail Activities', copy=True, auto_join=True)


# class HelpdeskSupportActivityLine(models.Model):
#     _name = 'helpdesk.support.activity.line'
#
#     activity_id = fields.Many2one('helpdesk.support.activity',
#                                   string='Activity',
#                                   required=True,
#                                   ondelete='cascade',
#                                   index=True, copy=False)
#
#     sequence = fields.Integer(required=True, default=10)
#     name = fields.Char(string='Level', required=True, copy=False)

class MaintenanceGuidelineActivity(models.Model):
    _inherit = 'maintenance.guideline.activity'

    support_level_id = fields.Many2one('helpdesk.support.level',
                                       string='Support level',
                                       required=False,
                                       ondelete='cascade',
                                       index=True, copy=False,
                                       check_company=True)


# Nivel de falla
class HelpdeskSupportLevel(models.Model):
    _name = 'helpdesk.support.level'
    _description = 'Helpdesk support level'
    _check_company_auto = True

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Level', required=True, copy=False)

    support_activity_ids = fields.One2many('maintenance.guideline.activity', 'support_level_id',
                                           string='Activities support', copy=True,
                                           auto_join=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
        except ValueError:
            default['name'] = self.name
        return super(HelpdeskSupportLevel, self).copy(default)
