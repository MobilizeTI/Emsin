# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleFuelLog(models.Model):
    _name = 'vehicle.fuel.log'
    _description = 'Vehicle fuel log'

    # Vehicle Details
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle', required=True)

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)

    # Refueling Details
    liter = fields.Float(string='Liter', required=False)

    fuel_tank_id = fields.Many2one(comodel_name='fuel.tank', string='Fuel Tank', required=True)

    @api.onchange('fuel_tank_id')
    def onchange_fuel_tank_id(self):
        self.price_x_liter = self.fuel_tank_id.average_price

    price_x_liter = fields.Float(string='Price per liter', required=False)

    @api.onchange('liter', 'price_x_liter')
    def onchange_price_x_liter(self):
        self.total_price = self.liter * self.price_x_liter

    total_price = fields.Float(string='Total price', required=False)

    # Odometer Details
    odometer_value = fields.Float(string='Odometer value', required=False)

    previous_odometer_reading = fields.Float(string='Previous odometer reading')

    flag_liters_process = fields.Boolean(required=False)

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        if self.vehicle_id:
            # record = self.search(
            #         [('vehicle_id', '=', self.vehicle_id.id)],
            #         order='date desc', limit=1)
            # if record:
            self.previous_odometer_reading = self.vehicle_id.odometer
        else:
            self.previous_odometer_reading = 0

    # Additional details
    date = fields.Date('Date', default=lambda self: fields.datetime.now().date(), required=True)
    invoice_reference = fields.Char(string='Invoice reference', required=False)

    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor', required=False)

    description = fields.Text(string="Description", required=False)

    def write(self, values):
        # Add code here
        res = super(VehicleFuelLog, self).write(values)

        if 'odometer_value' in values:
            odometer_value = values['odometer_value']
            self.vehicle_id.odometer = odometer_value
        self.vehicle_id.acquisition_date = self.date

        # value = self.fuel_tank_id.liters - self.liter
        self.fuel_tank_id.write(
            dict(
                last_filing_date=self.date,
                last_filing_price=self.price_x_liter,
                last_filing_amount=self.total_price,
                # liters=value,
            )
        )

        # self.fuel_tank_id._compute_liters(value=value)
        return res

    @api.model
    def create(self, values):
        # Add code here
        rec = super(VehicleFuelLog, self).create(values)
        rec.previous_odometer_reading = rec.vehicle_id.odometer
        rec.vehicle_id.odometer = rec.odometer_value
        rec.vehicle_id.acquisition_date = rec.date
        # value = rec.fuel_tank_id.liters - rec.liter
        rec.fuel_tank_id.write(
            dict(
                last_filing_date=rec.date,
                last_filing_price=rec.price_x_liter,
                last_filing_amount=rec.total_price,
                # liters=value,
            )
        )

        return rec

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.vehicle_id.name))
        return result

    @api.constrains('odometer_value')
    def _check_odometer_value(self):
        if any([log.odometer_value <= log.previous_odometer_reading for log in self]):
            raise ValidationError(_(f'Valor del odómetro atual debe ser mayor a anterior'))

# class OdometerValueHistory(models.Model):
#     _name = 'odometer.value.history'
#     _description = 'Odometer Value History'
#
#     name = fields.Char()
