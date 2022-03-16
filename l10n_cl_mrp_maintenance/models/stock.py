# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        return super(StockRule, self)._get_custom_move_fields() + [
            'maintenance_id',
        ]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    maintenance_id = fields.Many2one(related="group_id.maintenance_id",
                                     string="Maintenance Request", store=True,
                                     readonly=False)


class StockMove(models.Model):
    _inherit = "stock.move"

    maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request', index=True)

    system_class_id = fields.Many2one(
        'maintenance.system.classification',
        domain=[('allocation_level', '=', True)],
        string='Component', ondelete='restrict',
        required=False)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('maintenance_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.maintenance_id.id)
        return keys_sorted


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    pick_bom_pull_id = fields.Many2one('stock.rule', 'Picking Bill of Material Rule')

    def _get_global_route_rules_values(self):
        rules = super(StockWarehouse, self)._get_global_route_rules_values()

        rule = self.get_rules_dict()[self.id][self.delivery_steps]
        customer_loc, supplier_loc = self._get_partner_locations()
        production_location = self._get_production_location()

        rule = [r for r in rule if r.dest_loc == customer_loc][0]

        location_dest_id = production_location
        picking_type_id = rule.picking_type
        location_id = rule.from_loc

        rules.update({
            'pick_bom_pull_id': {
                'depends': ['delivery_steps'],
                'create_values': {
                    # set delivery route because we need be chained with the actual delivery routes
                    'route_id': self.delivery_route_id.id,
                    'procure_method': 'mts_else_mto',
                    'company_id': self.company_id.id,
                    'action': 'pull',
                    'auto': 'manual',
                },
                'update_values': {
                    'name': self._format_rulename(location_id, location_dest_id, 'BOM'),
                    'picking_type_id': picking_type_id.id,
                    'location_id': location_dest_id.id,
                    'location_src_id': location_id.id,
                    'active': True,
                },
            }
        })

        return rules

    @api.model
    def create_missing_global_routes_rules(self):
        warehouses = self.env['stock.warehouse'].search([])
        warehouse_without_pick_bom_pull_rules = warehouses.filtered(lambda w: not w.pick_bom_pull_id)
        for warehouse in warehouse_without_pick_bom_pull_rules:
            warehouse._create_or_update_global_routes_rules()
