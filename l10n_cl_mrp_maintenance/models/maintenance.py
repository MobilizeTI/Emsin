# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    request_bom = fields.Boolean("Request Bill of Material")
    require_bom = fields.Boolean("Require Bill of Material")
    require_employees = fields.Boolean("Require Validate Employees")
    require_valid_picking = fields.Boolean("Require Validate Pickings")
    require_valid_tasks = fields.Boolean("Require Validate Tasks")
    require_notify = fields.Boolean("Require Notify")


class MaintenanceGuideline(models.Model):
    _inherit = 'maintenance.guideline'

    bom_id = fields.Many2one('mrp.bom', 'Bill of Material',
                             check_company=True,
                             domain="[('type', '=', 'normal')]",
                             help="Bill of Materials allow you to define the list of required components to make a maintenance."
                             )


class MaintenanceTeam(models.Model):
    _inherit = 'maintenance.team'

    maintenance_location_id = fields.Many2one("stock.location", "Maintenance Location",
                                              domain="['|', ('company_id', '=', company_id), ('company_id', '=', False), ('usage', 'in', ['production', 'customer'])]"
                                              )


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.model
    def _default_maintenance_location(self):
        Location = self.env['stock.location']

        team = self.env['maintenance.team'].browse(self._get_default_team_id())
        maintenance_location = team.maintenance_location_id

        if not maintenance_location:
            maintenance_location = Location.sudo().search([
                ('usage', 'in', ['production', 'customer']),
                '|', ('company_id', '=', self.env.company.id),
                ('company_id', '=', False),
            ], limit=1)

        return maintenance_location

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, readonly=True,
                                   default=_default_warehouse_id, check_company=True
                                   )

    bom_ids = fields.Many2many('mrp.bom', 'Bills of Materials', compute='_compute_bom_ids')

    @api.depends('maintenance_guideline_ids')
    def _compute_bom_ids(self):
        for rec in self:
            bom_ids = []
            filtered = rec.maintenance_guideline_ids.filtered(lambda i: i.bom_id.exists())
            if filtered:
                bom_ids = [mg.bom_id.id for mg in filtered]
            rec.sudo().bom_ids = [(6, 0, bom_ids)]

    maintenance_location_id = fields.Many2one("stock.location", "Maintenance Location",
                                              check_company=True,
                                              domain="[('usage', 'in', ['production', 'customer'])]",
                                              default=_default_maintenance_location)
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    picking_ids = fields.One2many('stock.picking', 'maintenance_id', string='Transfers')
    picking_count = fields.Integer(string='BoM Transfers', compute='_compute_picking_count')

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for request in self:
            request.picking_count = len(request.picking_ids.filtered(
                lambda p: p.location_dest_id == request.maintenance_location_id)
            )

    @api.onchange('maintenance_team_id')
    def _onchange_maintenance_team(self):
        if self.maintenance_team_id and not self.maintenance_location_id:
            self.maintenance_location_id = self.maintenance_team_id.maintenance_location_id

    @api.constrains("stage_id")
    def _check_bom_stage(self):
        if self.stage_id.require_employees:
            task_not_employees = self.task_ids.filtered(lambda t: not t.employee_id.exists())
            if task_not_employees:
                raise ValidationError(
                    _(f'Las tareas relacionadas a {self.name} necesitan tener un empleado asignado para poder continuar'))

        if self.stage_id.request_bom:
            bom_request_without_done_pickings = self.filtered(
                lambda r: r.stage_id.require_bom and (
                        not r.picking_ids or any(p.state != 'done'
                                                 for p in r.picking_ids
                                                 if p.location_dest_id == r.maintenance_location_id)
                )
            )

            if bom_request_without_done_pickings and len(self.picking_ids) == 1:
                raise ValidationError(_(
                    "Los siguientes %s %s necesitan una solicitud de transferencia de lista de materiales procesada para poder continuar"
                ) % (
                                          _(self._description),
                                          ', '.join(bom_request_without_done_pickings.mapped('display_name')),
                                      ))
        if self.stage_id.require_valid_picking:
            pickings_not_done = self.picking_ids.filtered(lambda p: p.state != 'done')
            if len(pickings_not_done) > 0:
                raise ValidationError(
                    _('Tiene pickings que aún no han sido procesados relacionados con la solicitud {}'.format(self.name)))

        if self.stage_id.require_valid_tasks:
            task_not_done = self.task_ids.filtered(lambda p: p.stage_id.name not in ('Hecho', 'Cancelar'))
            if len(task_not_done) > 0:
                raise ValidationError(
                    _('Tiene tareas que aún no han sido procesadas relacionadas con la solicitud {}'.format(self.name)))

        data_filtered = self.filtered(lambda r: r.stage_id.request_bom and not r.picking_ids)
        data_filtered._action_launch_stock_rule()

    def action_view_delivery_bom(self):
        """
        This function returns an action that display existing delivery bom orders
        of given maintenance request ids. It can either be a in a list or in a form
        view, if there is only one delivery bom order to show.

         Esta función devuelve una acción que muestra las órdenes de entrega
         de las BoM existentes de los identificadores de solicitud de mantenimiento dados.
         Puede ser en una lista o en una vista de formulario, si sólo hay una orden de
         entrega de bom para mostrar.
        """
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]

        # pickings = self.mapped('picking_ids').filtered(
        #     lambda p: p.location_dest_id == p.group_id.maintenance_id.maintenance_location_id
        # )
        pickings = self.picking_ids
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]

        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id

        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]

        action['context'] = dict(
            self._context,
            default_picking_id=picking_id.id,
            default_picking_type_id=picking_id.picking_type_id.id,
            default_origin=self.name_seq,
            default_group_id=picking_id.group_id.id
        )

        return action

    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        maintenance request. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the maintenance request bom line product rule.

        Lanzar el método de ejecución del grupo de aprovisionamiento con los campos
        requeridos/personalizados generados por una solicitud de mantenimiento.
        El grupo de aprovisionamiento lanzará '_run_pull', '_run_buy' o '_run_manufacture'
        dependiendo de la regla de producto de la línea bom de la solicitud de mantenimiento.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        nonactive_test = False

        for request in self:
            products = []
            for bom in request.bom_ids:
                for line in bom.bom_line_ids:
                    products.append(line.product_id)

            if not request.bom_ids or not all(p.type in ('consu', 'product') for p in products):
                continue

            for bom in request.bom_ids:
                for line in bom.bom_line_ids:
                    qty = line.product_qty
                    if float_is_zero(qty, precision_digits=precision):
                        continue

                    group_id = request.procurement_group_id
                    if not group_id:
                        group_id = self.env['procurement.group'].create(request._prepare_procurement_group_vals())
                        request.procurement_group_id = group_id
                    else:
                        # In case the procurement group is already created and the request was
                        # cancelled, we need to update certain values of the group.
                        updated_vals = {}
                        # if group_id.partner_id != line.order_id.partner_shipping_id:
                        #     updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                        if group_id.move_type != 'one':
                            updated_vals.update({'move_type': 'one'})
                        if updated_vals:
                            group_id.write(updated_vals)

                    values = request._prepare_procurement_values(line, group_id=group_id)

                    # nonactive_test = nonactive_test or bool(self.maintenance_location_id and
                    #                                     self.maintenance_location_id.usage == 'production' and
                    #                                     self.warehouse_id)

                    procurements.append(self.env['procurement.group'].Procurement(
                        line.product_id,
                        qty,
                        line.product_uom_id,
                        request.maintenance_location_id,
                        line.display_name,
                        request.name,
                        request.company_id,
                        values
                    ))
        if procurements:
            self.env['procurement.group'].with_context(active_test=not nonactive_test).run(procurements)

        return True

    def _prepare_procurement_group_vals(self):
        return {
            'maintenance_id': self.id,
            'name': self.name,
            'move_type': 'one',
            # 'partner_id': self.order_id.partner_shipping_id.id,
        }

    def _prepare_procurement_values(self, line, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.

        Prepare la clave específica para los movimientos u otros componentes
        que se crearán a partir de una regla de stock procedente de una línea de
        pedido de venta. Este método puede ser anulado para añadir otras claves
        personalizadas que puedan ser utilizada en la creación de movimientos/po.
        """
        self.ensure_one()
        if not self.schedule_date:
            raise ValidationError(_(f'You must record the expected date for the request {self.name}'))
        date_planned = self.schedule_date

        values = {
            'warehouse_id': self.warehouse_id or False,
            'company_id': self.company_id,
            'date_planned': date_planned,
            # 'route_ids': self.route_id,
            'maintenance_id': self.id,
            'group_id': group_id,
        }

        # if self.maintenance_location_id and self.maintenance_location_id.usage == 'production' and self.warehouse_id:
        #     values.update(route_ids=self.warehouse_id._find_global_route('l10n_cl_mrp_maintenance.route_warehouse0_bom', _('Pickup BoM')))

        return values

    # Notificaciones
    @api.model
    def run_notify_user(self):
        notify_stage_ids = self.env['maintenance.stage'].sudo().search([('require_notify', '=', True)]).ids
        requests = self.sudo().search([('stage_id', 'in', notify_stage_ids),
                                       ('user_id', '!=', False),
                                       ('picking_count', '>', 0),
                                       ('company_id', '=', self.env.company.id)])

        for request in requests:
            for picking in request.picking_ids.filtered(
                    lambda p: p.state in ('draft', 'waiting', 'confirmed', 'assigned')):
                picking.action_assign()  # comprueba disponibilidad
                if picking.state == 'assigned':
                    link = f"""
                    <a href="/web#id={request.id}&action=345&model=maintenance.request&view_type=form" role="button" target="_blank">{request.name_seq}</a>
                    """
                    message = f'La lista de materiales para ({link}) está con stock disponible'
                    request.user_id.notify_success(message=message, title='Información', sticky=True)

        # request = self.browse(21)
        # message = 'The list of materials for the OT is with available stock'
        # request.user_id.notify_success(message=message, title='Information', sticky=True)
        # picking = self.env['stock.picking'].browse(20)
        # for rec in picking.move_ids_without_package:
        #     print(f'product: {rec.product_id.name} >>> demanda {rec.product_uom_qty} >>>reservado: {rec.forecast_availability}')
