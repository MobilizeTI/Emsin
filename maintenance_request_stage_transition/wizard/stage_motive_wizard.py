import logging

from odoo import fields, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StageMotiveWizard(models.TransientModel):
    _name = 'stage.motive.wizard'
    _description = "Stage Motive Wizard"

    stage_id = fields.Many2one('maintenance.stage', string='Stage')
    request_id = fields.Many2one('maintenance.request', string='OT')
    motive_id = fields.Many2one('maintenance.motive.stage', string='Motive',
                                required=True)
    comment = fields.Text('Comment:', required=False)

    def action_confirm(self):
        self.ensure_one()
        if self.request_id:
            self.request_id.sudo().write({
                'motive_log_ids': [(0, 0, {'motive_id': self.motive_id.id,
                                           'comment': self.comment,
                                           'request_id': self.request_id.id,
                                           'stage_name': self.stage_id.name,
                                           })
                                   ],
                'stage_id': self.stage_id.id
            })

            if self.stage_id.name == 'Diferido':
                self.sudo().request_id.is_deferred = True
            elif self.stage_id.name == 'En espera':
                self.sudo().request_id.is_waiting = True

            _logger.warning(
                f'>>> ot: {self.request_id.id}, {self.request_id.name_seq}, {self.request_id.name}, stage: {self.request_id.stage_id.name}')
        else:
            raise ValidationError("Internal error contact the support area")
