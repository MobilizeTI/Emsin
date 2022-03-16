# -*- coding: utf-8 -*-
from pprint import pprint

from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    _order = 'name_seq desc'

    # Usuario cliente -> Asignado a (ok)

    # ID ticket:
    name_seq = fields.Char(string='OT Reference', required=True, copy=False,
                           readonly=True,
                           index=True, default=lambda self: _('New'))

    # ID movil
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')

    # Tipo -> Tipo de ticket (ok)

    # Equipo
    equipment_id = fields.Many2one('maintenance.equipment',
                                   string='Equipment',
                                   related='vehicle_id.equipment_id')
    equipment_category_id = fields.Many2one('maintenance.equipment.category',
                                            string='Equipment Category',
                                            related='equipment_id.category_id')
    # Detalle del incidente -> Descripción del ticket (ok)

    # Nivel de falla
    failure_level_id = fields.Many2one('helpdesk.failure.level', string='Failure Level')

    # Nivel de soport
    support_level_ids = fields.Many2many('helpdesk.support.level', string='Support Levels')

    support_activity_ids = fields.Many2many('maintenance.guideline.activity',
                                            compute='_compute_support_activity_ids',
                                            string='Activities')

    place_of_care = fields.Char(string='Place of care', required=False, help="Barrio")

    @api.depends('support_level_ids')
    def _compute_support_activity_ids(self):
        for rec in self:
            support_activity_ids = []
            if rec.support_level_ids:
                activities = set()
                for record in rec.support_level_ids:
                    aux = set(record.support_activity_ids.ids)
                    activities = activities.union(aux)
                support_activity_ids = [(6, 0, list(activities))]
            rec.sudo().support_activity_ids = support_activity_ids

    # OT
    mtm_request_id = fields.Many2one('maintenance.request', string='Mtm_request_id', required=False)

    @api.model
    def create(self, values):
        # Add code here
        if values.get('name_seq', _('New')) == _('New'):
            name_seq = self.env['ir.sequence'].next_by_code('ticket.sequence')
            values.update(dict(name_seq=name_seq))
        return super(HelpdeskTicket, self).create(values)

    def action_create_ot(self):
        self.ensure_one()

        # action = self.env.ref('account.action_account_payments').read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('maintenance.hr_equipment_request_action')
        self.env.context = dict(self.env.context)
        self.env.context.update({'user_tkt_id': self.user_id.id, })
        context = dict(self._context)

        context.update({'default_name': self.name,
                        'default_partner_id': self.partner_id.id,
                        'default_user_id': self.user_id.id,
                        'default_ticket_id': self.id,
                        'default_equipment_id': self.equipment_id.id,
                        'default_create_type': 'ticket',
                        })
        # pprint(context)
        action['context'] = context

        res = self.env.ref('maintenance.hr_equipment_request_view_form', False)
        form_view = [(res and res.id or False, 'form')]
        action['views'] = form_view
        # action['res_id'] = self.id
        action['target'] = 'current'
        #
        return action

    @api.model
    def action_create_by_monthly_pdf(self, opc=None):
        data = {
            'model_id': self.id,
            'opc': opc
        }
        return self.env.ref('mblz_mueve.action_report_monthly_tickets_pdf_by_month').report_action(self, data=data)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        level0 = self.env['helpdesk.support.level'].sudo().search([('name', '=ilike', 'Nivel 0')], limit=1)
        # defaults['user_id'] = self.env.user.id
        if level0:
            defaults.update({
                'support_level_ids': [(6, 0, [level0.id])],
            })
        return defaults
