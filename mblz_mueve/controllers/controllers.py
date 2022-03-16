# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_helpdesk.controllers.main import WebsiteHelpdesk
from odoo.http import request


class WebsiteHelpdesk2(WebsiteHelpdesk):

    @http.route(['/helpdesk/', '/helpdesk/<model("helpdesk.team"):team>'], type='http', auth="user", website=True,
                sitemap=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        user = request.env.user
        if not user.flag_crete_tkt_portal:
            OBJ_CFG = request.env['ir.config_parameter'].sudo()
            email_portal = OBJ_CFG.get_param('mblz_mueve.email_portal')
            # print(email_portal)
            return request.render("mblz_mueve.heldesk_error", {'email_portal': email_portal})

        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].search(
            ['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True),
             ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        result['default_partner_values'] = self._get_partner_data()
        return request.render("website_helpdesk.team", result)
