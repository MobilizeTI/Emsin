# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    # _inherits = 'image.mixin'

    image = fields.Binary(string="Image", attachment=True)

    mbfm_custom = fields.Selection(
        [('hours', 'Hours'), ('days', 'Days')],
        string='MTBF Metric', default="days",
        help='Mean Time Between Failure Measure')

    def _register_hook(self):
        """ Patch models to correct the that should trigger """

        def make__compute_maintenance_request():
            """ Instanciate the _compute_maintenance_request. """

            @api.depends('mbfm_custom')
            def _compute_maintenance_request(self):
                for equipment in self:
                    maintenance_requests = equipment.maintenance_ids.filtered(
                        lambda x: x.maintenance_type == 'corrective' and x.stage_id.done
                    )
                    mttr_days_factor = 1 if equipment.mbfm_custom == 'days' else 24
                    mttr_days = 0

                    for maintenance in maintenance_requests:
                        if maintenance.stage_id.done and maintenance.close_date:
                            mttr_days += (maintenance.close_date - maintenance.request_date).days * mttr_days_factor

                    equipment.mttr = len(maintenance_requests) and (mttr_days / len(maintenance_requests)) or 0

                    maintenance = maintenance_requests.sorted(lambda x: x.request_date)

                    if len(maintenance) >= 1:
                        equipment.mtbf = (maintenance[
                                              -1].request_date - equipment.effective_date).days * mttr_days_factor / len(
                            maintenance)

                    equipment.latest_failure_date = maintenance and maintenance[-1].request_date or False

                    if equipment.mtbf:
                        if equipment.mbfm_custom == 'days':
                            equipment.estimated_next_failure = equipment.latest_failure_date + relativedelta(
                                days=equipment.mtbf)
                        else:
                            equipment.estimated_next_failure = equipment.latest_failure_date + relativedelta(
                                hours=equipment.mtbf)
                    else:
                        equipment.estimated_next_failure = False

            return _compute_maintenance_request

        bases = type(self).mro()
        bases.reverse()
        make_patched_methods = [(method_name[5:], method_patch)
                                for method_name, method_patch in locals().items()
                                if 'make_' in method_name]

        for base in bases:
            if hasattr(base, '_name') and base._name == self._name:
                methods_2patch = [(method_name, method_patch)
                                  for method_name, method_patch in make_patched_methods
                                  if hasattr(base, method_name)]

                for method_name, method_patch in methods_2patch:
                    base._patch_method(method_name, method_patch())
                    patched_method = getattr(base, method_name)
                    patched_method.origin_base = base
                    # mark the method as patched
                    make_patched_methods.remove((method_name, method_patch))

            if not make_patched_methods:
                break

        super(MaintenanceEquipment, self)._register_hook()


class MaintenanceEquipmentIMage(models.Model):
    _name = 'maintenance.equipment.image'
    _description = 'maintenance equipment image'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', ondelete='cascade', index=True,
                                   check_company=True)

    image = fields.Binary(string="Image", attachment=True)
