# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AddLitersWizard(models.TransientModel):
    _name = 'add.liters.wizard'
    _description = 'Add Liters Wizard'

    liters = fields.Float(
        string='Liters',
        required=True)

    price_x_liter = fields.Float(
        string='Price per liter',
        required=True)

    def action_create_history(self):
        active_id = self._context.get('active_id')
        if active_id:
            fuel_tank = self.env['fuel.tank'].browse(active_id)
            fuel_tank.fuel_filling_history_ids = [(0, 0, dict(
                fuel_tank_id=fuel_tank.id,
                liters=self.liters,
                price_x_liter=self.price_x_liter,
            ))]
            value = fuel_tank.liters+self.liters
            fuel_tank.liters = value

            fuel_tank.last_added_fuel_date = fields.Datetime.now()
