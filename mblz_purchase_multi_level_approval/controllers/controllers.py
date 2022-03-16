# -*- coding: utf-8 -*-
# from odoo import http


# class MblzPurchaseMultiLevelApproval(http.Controller):
#     @http.route('/mblz_purchase_multi_level_approval/mblz_purchase_multi_level_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mblz_purchase_multi_level_approval/mblz_purchase_multi_level_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mblz_purchase_multi_level_approval.listing', {
#             'root': '/mblz_purchase_multi_level_approval/mblz_purchase_multi_level_approval',
#             'objects': http.request.env['mblz_purchase_multi_level_approval.mblz_purchase_multi_level_approval'].search([]),
#         })

#     @http.route('/mblz_purchase_multi_level_approval/mblz_purchase_multi_level_approval/objects/<model("mblz_purchase_multi_level_approval.mblz_purchase_multi_level_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mblz_purchase_multi_level_approval.object', {
#             'object': obj
#         })
