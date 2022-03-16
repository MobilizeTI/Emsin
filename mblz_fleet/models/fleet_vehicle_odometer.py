from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning, UserError
from datetime import datetime, timedelta


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    odometer_actual = fields.Float(related='vehicle_id.odometer', string='Odometer actual')
    value_dif = fields.Float('Value net', readonly=True)

    def _valida_value(self, value, date, vehicle_id=False, opc=False):
        # si opc = False significa que se esta creando sino actualizando
        def _valid_odoo_day(limit_odometer, value_dif, vh):
            day = date.day
            odoo_all_vehicle = self.search([('vehicle_id', '=', vh.id)])

            sum_odoo_day = sum(odoo_all_vehicle.filtered(lambda l: l.date.day == day).mapped('value_dif'))
            sum_odoo_day += value_dif
            if sum_odoo_day > limit_odometer:
                raise UserError(
                    f"La suma total registrada  {sum_odoo_day}, supera el límite diario permitido de {limit_odometer} para el vehículo {vh.name}")

        def _valid_limit_odoo(vh):
            limit_odometer = int(self.env['ir.config_parameter'].sudo().get_param('mblz_fleet.limit_odometer'))
            value_dif = value - vh.odometer
            _valid_odoo_day(limit_odometer, value_dif, vh)

            if value_dif > limit_odometer:
                raise UserError(
                    f'El valor añadído {value_dif} es mayor al límite de registro de odómetro permitido: {limit_odometer} para el vehículo {vh.name}')
            return value_dif if not opc else value_dif + self.value_dif

        if not vehicle_id:
            value_dif = _valid_limit_odoo(self.vehicle_id)
            return value > self.vehicle_id.odometer, value_dif
        else:
            value_dif = _valid_limit_odoo(vehicle_id)
            return value > vehicle_id.odometer, value_dif

    @api.model
    def create(self, values):
        # Add code here
        if 'value' and 'vehicle_id' and 'date' in values:
            value = values.get('value', 0.0)
            date = datetime.strptime(values.get('date', False), "%Y-%m-%d")
            vehicle_id = values.get('vehicle_id', False)
            vehicle_id = self.vehicle_id.sudo().browse(vehicle_id)
            valid, value_dif = self._valida_value(value, date, vehicle_id)
            if not valid:
                raise ValidationError(
                    f'El valor {value} debe ser mayor al odómetro actual: {vehicle_id.odometer} para el vehículo {vehicle_id.name}')
            values['value_dif'] = value_dif
        return super(FleetVehicleOdometer, self).create(values)

    def write(self, values):
        # Add code here
        if 'value' in values:
            value = values.get('value', 0.0)
            valid, value_dif = self._valida_value(value, date=self.date, opc=True)
            if not valid:
                raise ValidationError(
                    f'El valor {value} debe ser mayor al odómetro actual: {self.vehicle_id.odometer} para el vehículo {self.vehicle_id.name}')
            values['value_dif'] = value_dif
        return super(FleetVehicleOdometer, self).write(values)
