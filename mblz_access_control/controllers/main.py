# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import Home, ensure_db, redirect_with_hash
from odoo.http import request


class MblzHome(Home, http.Controller):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if kw.get('debug') == "assets" or kw.get('debug') == '1':
            user = request.env.user.browse(request.session.uid)
            if not user.hide_debug_assets_permission and not user._is_admin():
                return redirect_with_hash('/web?debug=0')
        return super(MblzHome, self).web_client(s_action=s_action, **kw)
      