import base64
import io

from xlsxwriter import Workbook

from odoo import api, fields, models, tools, _
import datetime

from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    request_task_id = fields.Many2one('maintenance.request.task', 'Task request')
    wz_material_add_id = fields.Many2one('request.materials.additional', 'Wz Materials Additional')
    product_line_task_ids = fields.Many2many('task.line.materials', compute='_compute_product_line_task_ids')

    @api.depends('request_task_id', 'wz_material_add_id')
    def _compute_product_line_task_ids(self):
        for rec in self:
            if rec.request_task_id and rec.wz_material_add_id:
                materials = rec.request_task_id.product_line_ids.filtered(
                    lambda l: l.wz_material_add_id.id == rec.wz_material_add_id.id)
                if materials:
                    rec.product_line_task_ids = [(6, 0, materials.ids)]
            else:
                rec.product_line_task_ids = [(6, 0, [])]

    def action_approve(self, approver=None):
        super(ApprovalRequest, self).action_approve(approver)
        if self.request_task_id:
            self.create_picking()

    def action_refuse(self):
        super(ApprovalRequest, self).action_refuse()
        # if self.request_task_id:
        #     self.request_task_id.state_to_denied()

    def create_picking(self):
        # se crea el picking con la solicitud aprovada
        obj_stock_picking = self.env['stock.picking'].sudo()

        # Se crea una transferencia salida de sl-tienda ->OUT
        wh_default = self.env.ref('stock.warehouse0')

        picking_type_id = self.env['stock.picking.type'].sudo().search(
            [('code', '=', 'outgoing'),
             ('sequence_code', '=', 'OUT'),
             ('company_id', '=', self.company_id.id),
             ('warehouse_id', '=', wh_default.id)], limit=1)
        location_id = self.env.ref('stock.stock_location_stock').id
        location_dest_id = self.request_task_id.request_maintenance_location_id.id

        moves = []
        for line in self.product_line_task_ids:
            moves.append((0, 0, {
                'name': line.product_id.name,
                'product_uom': line.product_uom_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_qty,
                'system_class_id': line.system_class_id.id,
                'company_id': self.company_id.id,
                'picking_type_id': picking_type_id.id,
            }))
        values = {
            'partner_id': self.request_task_id.user_id.partner_id.id,
            'picking_type_id': picking_type_id.id,
            'origin': self.request_task_id.request_id.name_seq,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_ids_without_package': moves,
        }

        stock_picking = obj_stock_picking.create(values)

        if stock_picking.exists():
            stock_picking.action_confirm()
            stock_picking.action_assign()
        #     wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, stock_picking.id)]})
        #     wiz.process()
        self.request_task_id.picking_ids = [(4, stock_picking.id)]
        self.request_task_id.request_id.picking_ids = [(4, stock_picking.id)]
