# -*- coding: utf-8 -*-
# from odoo import http


# class MblzFleet(http.Controller):
#     @http.route('/mblz_fleet/mblz_fleet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mblz_fleet/mblz_fleet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mblz_fleet.listing', {
#             'root': '/mblz_fleet/mblz_fleet',
#             'objects': http.request.env['mblz_fleet.mblz_fleet'].search([]),
#         })

#     @http.route('/mblz_fleet/mblz_fleet/objects/<model("mblz_fleet.mblz_fleet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mblz_fleet.object', {
#             'object': obj
#         })
