import werkzeug.exceptions

from odoo import api, fields, models
from odoo.tools.translate import html_translate


class Menu(models.Model):
    _inherit = "website.menu"

    def _compute_visible(self):
        for menu in self:
            visible = True
            if menu.page_id and not menu.user_has_groups('base.group_user') and \
                    (not menu.page_id.sudo().is_visible or
                     (not menu.page_id.view_id._handle_visibility(do_raise=False) and
                      menu.page_id.view_id.visibility != "password")):
                visible = False

            if menu.url == '/helpdesk/':
                visible = False
            menu.is_visible = visible
