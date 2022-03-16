# -*- coding: utf-8 -*-


from odoo.http import request
from odoo import models, api

import base64

from odoo import fields, api, models
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter

from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, format_date
import requests
import json
import pytz

fmt = '%Y-%m-%d %H:%M:%S'
fmt_date = '%Y-%m-%d'

MONTH_SELECTION = [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'),
                   ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'),
                   ('11', 'Noviembre'), ('12', 'Diciembre')]


class MonthlyTicketsPdf(models.AbstractModel):
    _name = 'report.mblz_mueve.report_monthly_tickets_pdf'
    _description = 'report_monthly_tickets_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        HT = self.env['helpdesk.ticket'].sudo()
        tickets = HT.search([('stage_id.is_close', '=', False), ('company_id', '=', self.env.company.id)])
        monthly_tickets = tickets.filtered(lambda t: t.create_date.month == fields.Datetime.now().month)

        data_tickets = []
        for ticket in monthly_tickets:
            data_tickets.append({
                'name': ticket.name,
                'name_seq': ticket.name_seq,
                'team_name': ticket.team_id.name,
                'user_name': ticket.user_id.name,
                'type': ticket.ticket_type_id.name,
                'vehicle_name': ticket.vehicle_id.name,
                'categories': ', '.join(map(str, ticket.tag_ids.mapped('name'))),
                'ot_name': ticket.mtm_request_id.name,
                'partner_name': ticket.partner_id.name,
                'partner_email': ticket.partner_id.name,
                'failure_level': ticket.failure_level_id.name,
                'support_level': ', '.join(map(str, ticket.support_level_ids.mapped('name'))),
                'email_cc': ticket.email_cc,

                # fecha y hora
                'create_date': ticket.create_date.strftime(fmt_date),

                # tiempo de atención a las solicitudes por todos los canales
                'attention_time': '',

                # relación de todos los insidentes ?

                # tipo de solución a cada insidente ?
                'solution_type': '',

                # tiempo de solución a cada incidente y cierre del ticket?
                'solution_time': '',

                # lugar de atención de cada insidente
                'place_attention': '',

                # acción realizada para la solución
                'action_performed': '',
            })

        return {
            'name_report': f'TICKET DE SOPORTE MES {[m[1] for m in MONTH_SELECTION][fields.Datetime.now().month - 1]}'.upper(),
            'docs': data_tickets,
        }
