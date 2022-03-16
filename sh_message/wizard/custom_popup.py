from odoo import api, fields, models, _, exceptions

WARNING_TYPES = [('warning', 'Advertencia'), ('info', 'Información'), ('error', 'Error')]


class CustomWarning(models.TransientModel):
    _name = 'custom.warning'
    _description = 'warning - message'
    _req_name = 'title'

    my_type = fields.Selection(WARNING_TYPES, string='Type', readonly=True)
    title = fields.Char(string="Title", size=100, readonly=True)
    my_message = fields.Text(string="Message", readonly=True)

    def message(self, id, context):
        message = self.browse(id)
        message_type = [t[1] for t in WARNING_TYPES if message.id.my_type == t[0]][0]
        res = {
            'name': '%s: %s' % (_(message_type), _(message.id.title)),
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'custom.warning',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': message.id.id
        }
        return res

    @api.model
    def warning(self, title, message, context=None):
        id = self.create({'title': title, 'my_message': message, 'my_type': 'warning'})
        res = self.message(id, context)
        return res

    @api.model
    def info(self, title, message, context=None):
        id = self.create({'title': title, 'my_message': message, 'my_type': 'info'})
        res = self.message(id, context)
        return res

    @api.model
    def error(self, title, message, context=None):
        id = self.create({'title': title, 'my_message': message, 'my_type': 'error'})
        res = self.message(id, context)
        return res
