# -*- coding: utf-8 -*-
# from odoo import http


# class MblzTires(http.Controller):
#     @http.route('/mblz_tires/mblz_tires/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mblz_tires/mblz_tires/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mblz_tires.listing', {
#             'root': '/mblz_tires/mblz_tires',
#             'objects': http.request.env['mblz_tires.mblz_tires'].search([]),
#         })

#     @http.route('/mblz_tires/mblz_tires/objects/<model("mblz_tires.mblz_tires"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mblz_tires.object', {
#             'object': obj
#         })
