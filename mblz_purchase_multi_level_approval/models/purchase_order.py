# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    document_approval_id = fields.Many2one('document.approval', string='Document approval default')
    flag_approval_multi = fields.Boolean(string='Is approval multi level', compute='_compute_flag_approval_multi')
    flag_user_approval = fields.Boolean(string='My orders to approve', compute='_compute_flag_approval_multi')

    @api.depends('document_approval_id')
    def _compute_flag_approval_multi(self):
        for po in self:
            OBJ_CFG = po.env['ir.config_parameter'].sudo()
            flag_approval_multi = OBJ_CFG.get_param('mblz_purchase_multi_level_approval.po_multi_level_approval')
            po.sudo().flag_approval_multi = flag_approval_multi
            line_user = po.approval_user_ids.filtered(lambda l: l.user_id.id == po.env.user.id)
            if line_user:
                flag_user_approval = not line_user.approve
            else:
                flag_user_approval = False
            po.sudo().flag_user_approval = flag_user_approval

    approval_user_ids = fields.One2many('purchase.approval.line', 'order_id', string='Approvals', copy=True)
    users_approvals = fields.Many2many('res.users', string='users_approvals')

    @api.onchange('amount_total')
    def onchange_amount_total_approvals(self):
        self._set_approvals()

    def _set_approvals(self):
        doc_users = set()
        lines = self.document_approval_id.doc_approval_ids.filtered(lambda l: self.amount_total >= l.amount)
        for record in lines:
            for user in record.user_ids:
                doc_users.add(user.id)
        data_approvals = []
        self.users_approvals = [(6, 0, list(doc_users))]
        for user in doc_users:
            data_approvals.append((0, 0, {'order_id': self.id, 'user_id': user}))
        self.sudo().update(dict(approval_user_ids=[(6, 0, [])]))
        self.sudo().update(dict(approval_user_ids=data_approvals))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        OBJ_CFG = self.env['ir.config_parameter'].sudo()
        po_multi_level_approval = OBJ_CFG.get_param('mblz_purchase_multi_level_approval.po_multi_level_approval')
        document_approval_id = int(OBJ_CFG.get_param('mblz_purchase_multi_level_approval.document_approval_id'))
        if po_multi_level_approval and document_approval_id:
            res['document_approval_id'] = document_approval_id
        return res

    flag_user_approved = fields.Boolean(string='flag_user_approved', compute='_compute_flag_user_approved')

    @api.depends('approval_user_ids')
    def _compute_flag_user_approved(self):
        for record in self:
            line_user = record.approval_user_ids.filtered(lambda l: l.user_id.id == record.env.user.id)
            record.flag_user_approved = line_user.approve

    def action_approve_rfq(self):
        return self.action_down_approve_rfq(approve=True)
        # line_user = self.approval_user_ids.filtered(lambda l: l.user_id.id == self.env.user.id)
        # if line_user:
        #     line_user.approve = True

    def action_down_approve_rfq(self, approve=False):
        view = self.env.ref('mblz_purchase_multi_level_approval.wz_approve_view_form', False)
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['default_order_id'] = self.id
        context['default_flag_approve'] = approve
        return {
            # 'name': _('Info'),
            'type': 'ir.actions.act_window',
            'res_model': 'wz.approve',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }
        # line_user = self.approval_user_ids.filtered(lambda l: l.user_id.id == self.env.user.id)
        # if line_user and self.flag_user_approved:
        #     line_user.approve = False
        #     self.flag_user_approved = False

    flag_approve_admin = fields.Boolean(string='Approve for user admin', required=False)

    def button_confirm(self):
        if self.flag_approval_multi and not self.is_complete_approve:
            if self.env.user.id in self.document_approval_id.user_admin_ids.ids:
                for line in self.approval_user_ids:
                    line.approve_admin = True
                    self.flag_approve_admin = True
            elif not self.is_complete_approve:
                raise ValidationError(_('The purchase order is pending validation!'))
        return super().button_confirm()

    # barra de programación
    user_approve_percent = fields.Float('Approve percentage', compute='_compute_user_approve_percent',
                                        help='Percentage of users approve')

    @api.depends('approval_user_ids')
    def _compute_user_approve_percent(self):
        for rec in self:
            user_approve_percent = 0
            if rec.approval_user_ids:
                cant_users = len(rec.approval_user_ids)
                count_user_approve = len(rec.approval_user_ids.filtered(lambda l: l.approve))
                value = (count_user_approve / cant_users) * 100
                user_approve_percent = value
            rec.sudo().user_approve_percent = user_approve_percent

    is_complete_approve = fields.Boolean(string='Complete approval', compute='_compute_is_complete_approve')

    @api.depends('approval_user_ids')
    def _compute_is_complete_approve(self):
        for record in self:
            record.is_complete_approve = all(record.approval_user_ids.mapped('approve'))

    # notificar a los usuarios que no han aprobado aún la RFQ
    def notify_user_approve(self):
        # notificar al usuario
        link = f"""
                                <a href="/web#id={self.id}&action=583&model=purchase.order&view_type=form" role="button" target="_blank">{self.name}</a>
                                """
        message = f'Orden de compra ({link}) para su aprobación!'
        users_notify = self.approval_user_ids.filtered(lambda l: not l.approve and l.user_id.id != self.env.user.id)
        for line in users_notify:
            line.user_id.notify_warning(message=message, title=_('Warning'), sticky=True)


class PurchaseApprovalLine(models.Model):
    _name = 'purchase.approval.line'
    _description = 'Purchase Approval Line'

    sequence = fields.Integer(required=True, default=10)
    order_id = fields.Many2one('purchase.order', string='Order reference', required=True,
                               ondelete='cascade',
                               index=True, copy=False)
    user_id = fields.Many2one(comodel_name='res.users', string='Approver', required=True)
    approve = fields.Boolean(string='Approve user', required=False)
    approve_admin = fields.Boolean(string='Approve Admin', required=False)
    comment = fields.Text(string="Comment user", required=False)
