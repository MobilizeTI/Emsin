# -*- coding: utf-8 -*-

from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class SchedulerOTNew(models.TransientModel):
    _name = 'scheduler.ot.new'
    _description = 'Run Scheduler OT Manually'

    def button_run_cron(self):
        cron_id = self.env.ref('l10n_cl_maintenance.maintenance_request_cron')
        if cron_id.exists():
            cron_id.sudo().method_direct_trigger()
        return {'type': 'ir.actions.act_window_close'}
