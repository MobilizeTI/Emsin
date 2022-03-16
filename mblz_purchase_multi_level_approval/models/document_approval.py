# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DocumentApproval(models.Model):
    _name = 'document.approval'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Document Approval -multi level'
    _check_company_auto = True

    # company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    name = fields.Char('Name document')
    doc_approval_ids = fields.One2many(comodel_name='document.approval.line', inverse_name='doc_approval_id',
                                       string='Lines', required=True)
    user_admin_ids = fields.Many2many('res.users', string='Users admin')
    # partner_ids = fields.Many2many('res.partner', string='Partners', check_company=True)
    # product_ids = fields.Many2many('product.product', string='Products', check_company=True)


class DocumentApprovalLine(models.Model):
    _name = 'document.approval.line'
    _description = 'Document Approval Line'

    sequence = fields.Integer(required=True, default=10)
    doc_approval_id = fields.Many2one('document.approval', string='Document reference', required=True,
                                      ondelete='cascade',
                                      index=True, copy=False)
    # company_id = fields.Many2one('res.company', related='doc_approval_id.company_id')
    amount = fields.Float(string='Total greater than or equal', required=True, help='Total greater than or equal')
    user_ids = fields.Many2many('res.users', string='Approvers', required=True)
