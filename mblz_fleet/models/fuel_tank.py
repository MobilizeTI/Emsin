# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FuelTank(models.Model):
    _name = 'fuel.tank'
    _description = 'Fuel Tank'

    # Tank Details
    name = fields.Char(string='Name', required=True)
    location = fields.Char(string='Location', required=False)
    last_clean_date = fields.Datetime(string='Last clean date', required=False)

    # Fuel Details
    capacity = fields.Integer(string='Capacity', required=False)
    liters = fields.Float(string='Liters', compute='_compute_liters')

    @api.depends('fuel_filling_history_ids')
    def _compute_liters(self):
        for rec in self:
            liters = 0
            if rec.fuel_filling_history_ids:
                liters = sum(rec.fuel_filling_history_ids.mapped('liters'))
                fuel_log = rec.env['vehicle.fuel.log'].search([])
                fuel_log_filter = fuel_log.filtered(lambda l: l.fuel_tank_id.id == rec.id and not l.flag_liters_process)
                liters_process = 0
                for log in fuel_log:
                    liters_process += log.liter
                    log.flag_liters_process = True
                liters = liters - liters_process
            rec.liters = liters

    average_price = fields.Float(string='Average price', compute='_compute_average_price')

    @api.depends('fuel_filling_history_ids')
    def _compute_average_price(self):
        for rec in self:
            average_price = 0
            if rec.fuel_filling_history_ids:
                sum_price_x_liter = sum(rec.fuel_filling_history_ids.mapped('price_x_liter'))
                average_price = sum_price_x_liter / (len(rec.fuel_filling_history_ids))
            rec.average_price = int(average_price)

    # def _default_uom_id_liter(self):
    #     return self.env.ref('u
    #     om.product_uom_litre').id

    # uom_id = fields.Many2one('uom.uom', string="UOM", default=_default_uom_id_liter)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.lang_es_CO').id)

    # Last Filling Details
    last_filing_date = fields.Date(string='Last filing date', copy=False)
    last_filing_amount = fields.Float(string='Last filing amount', copy=False)
    last_filing_price = fields.Float(string='Last filing price', copy=False)

    # Consumption Details
    total_filling_fuel = fields.Float(
        string='Total filling fuel',
        compute='_compute_total_filling_fuel')

    @api.depends('capacity', 'liters')
    def _compute_total_filling_fuel(self):
        for rec in self:
            total_filling_fuel = 0
            if rec.capacity and rec.liters:
                total_filling_fuel = (rec.liters * 1) / rec.capacity

            rec.total_filling_fuel = total_filling_fuel

    last_added_fuel_date = fields.Datetime(
        string='Last added fuel date',
        readonly=True, copy=False, help='Date of last fuel added')

    fuel_filling_history_ids = fields.One2many(
        comodel_name='fuel.filling.history',
        inverse_name='fuel_tank_id',
        string='Fuel Filling History',
        required=False)

    def button_create_history(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Add Liters'),
                'res_model': 'add.liters.wizard',
                'target': 'new',
                'view_mode': 'form',
                }

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        try:
            default.setdefault('name', _("%s (copy)") % (self.name or ''))
        except ValueError:
            default['name'] = self.name
        return super(FuelTank, self).copy(default)


class FuelFillingHistory(models.Model):
    _name = 'fuel.filling.history'
    _description = 'Fuel Filling History'
    _order = 'date'

    date = fields.Datetime('Date time',
                           default=lambda self: fields.datetime.now(), required=True)
    fuel_tank_id = fields.Many2one('fuel.tank',
                                   ondelete='cascade',
                                   string='Task', required=False)

    liters = fields.Float(string='Liters', required=True)

    price_x_liter = fields.Float(string='Price per liter', required=True)
