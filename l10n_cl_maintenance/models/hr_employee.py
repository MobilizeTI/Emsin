from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    speciality_ids = fields.Many2many('hr.specialty.tag',
                                      string='Specialities', required=False)

    availability = fields.Selection(
        string='Availability',
        selection=[('available', 'Available'),
                   ('no available', 'No available'), ],
        required=True, default='available')

    @api.onchange('availability')
    def onchange_availability(self):
        if self.user_id:
            # FEXME//: debería buscar si el todas las tareas en las cuales el usuario esta asignado y no esta hecha
            tasks_employee = self.env['maintenance.request.task'].sudo().search([
                ('user_id', '=', self.user_id.id),
                ('is_closed', '=', False),
                ('company_id', '=', self.env.company.id)])

            task = tasks_employee.filtered(lambda l: l.request_id.user_id.exists())
            users = set()
            for req in task:
                users.add(req.request_id.user_id)
            for user in users:
                if self.availability == 'no available' and task.request_id.user_id:
                    message = f"El técnico {self.name} no está disponible"
                    user.notify_danger(message=message, title=_('Warning'), sticky=True)

                else:
                    message = f"El técnico {self.name} está disponible"
                    user.notify_success(message=message, title=_('Information'), sticky=True)
