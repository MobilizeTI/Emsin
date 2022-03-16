# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    po_multi_level_approval = fields.Boolean("Purchase Order Approval Multi Level")
    document_approval_id = fields.Many2one('document.approval', string='Document approval default')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('mblz_purchase_multi_level_approval.po_multi_level_approval',
                                                  self.po_multi_level_approval)
        self.env['ir.config_parameter'].set_param('mblz_purchase_multi_level_approval.document_approval_id',
                                                  self.document_approval_id.id)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        OBJ_CFG = self.env['ir.config_parameter'].sudo()
        po_multi_level_approval = OBJ_CFG.get_param('mblz_purchase_multi_level_approval.po_multi_level_approval')
        document_approval_id = int(OBJ_CFG.get_param('mblz_purchase_multi_level_approval.document_approval_id'))
        if po_multi_level_approval and document_approval_id:
            res.update(
                po_multi_level_approval=po_multi_level_approval,
                document_approval_id=document_approval_id,
            )
        return res
