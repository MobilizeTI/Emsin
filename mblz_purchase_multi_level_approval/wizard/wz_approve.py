# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WZApprove(models.TransientModel):
    _name = 'wz.approve'
    _description = 'Wizard Approve'

    order_id = fields.Many2one('purchase.order', string='Order reference', required=True)
    comment = fields.Text(string="Comment", required=False)
    flag_approve = fields.Boolean(string='flag_approve', required=False)

    def action_confirm(self):
        line_user = self.order_id.approval_user_ids.filtered(lambda l: l.user_id.id == self.env.user.id)
        line_user.comment = self.comment
        if self.flag_approve and line_user:
            line_user.approve = True
        else:
            if line_user and self.order_id.flag_user_approved:
                line_user.approve = False
                self.order_id.flag_user_approved = False
