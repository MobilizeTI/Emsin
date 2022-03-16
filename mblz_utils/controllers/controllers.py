# -*- coding: utf-8 -*-
# from odoo import http


# class MblzUtils(http.Controller):
#     @http.route('/mblz_utils/mblz_utils/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mblz_utils/mblz_utils/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mblz_utils.listing', {
#             'root': '/mblz_utils/mblz_utils',
#             'objects': http.request.env['mblz_utils.mblz_utils'].search([]),
#         })

#     @http.route('/mblz_utils/mblz_utils/objects/<model("mblz_utils.mblz_utils"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mblz_utils.object', {
#             'object': obj
#         })
