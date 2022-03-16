from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class MaintenanceRequestTask(models.Model):
    _inherit = 'maintenance.request.task'

    request_maintenance_location_id = fields.Many2one(related='request_id.maintenance_location_id')
    # Lista de materiales adicionales
    product_line_ids = fields.One2many('task.line.materials', 'task_id', 'Product Lines', copy=True)

    approval_ids = fields.One2many('approval.request', 'request_task_id', string='Approvals', required=False)

    picking_ids = fields.Many2many('stock.picking', string='Pickings', required=False)

    picking_count = fields.Integer(compute='_compute_picking_count')
    approval_count = fields.Integer(compute='_compute_approval_count')

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for task in self:
            task.sudo().picking_count = len(task.picking_ids)

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for task in self:
            task.sudo().approval_count = len(task.approval_ids)

    @api.constrains("stage_id")
    def _check_picking_stage(self):
        pickings_stage = self.picking_ids.filtered(lambda p: p.state != 'done')
        if len(pickings_stage) > 0:
            raise ValidationError(_('You have pickings that have not yet been processed related to the task'))
        self.env.context = dict(self.env.context)
        self.env.context.update({'flag_update_picking_from_task': True})

    def get_pickings(self):
        action = self.env.ref('stock.action_picking_tree_all').with_user(SUPERUSER_ID).read()[0]
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
            default_origin=self.name,
            default_group_id=picking_id.group_id.id
        )

        return action

    def get_approvals(self):
        action = self.env.ref('approvals.approval_request_action_all').sudo().read()[0]
        approvals = self.approval_ids
        if len(approvals) > 1:
            action['domain'] = [('id', 'in', approvals.ids)]

        elif approvals:
            form_view = [(self.env.ref('approvals.approval_request_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = approvals.id
        return action

    def button_create_approval_request(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Create Request Materials Additional'),
                'res_model': 'request.materials.additional',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_task_id': self.id},
                }

    @api.constrains("stage_id")
    def _check_pickings_stage(self):
        if self.stage_id.require_valid_picking:
            pickings_not_done = self.picking_ids.filtered(lambda p: p.state != 'done')
            if len(pickings_not_done) > 0:
                raise ValidationError(
                    _('You have pickings that have not yet been processed related to the request {}'.format(self.name)))


class TaskLineMaterials(models.Model):
    _name = 'task.line.materials'
    _order = "sequence, id"
    _rec_name = "product_id"
    _description = 'Product of Material Line'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', 'Company', index=True,
                                 default=lambda self: self.env.company)

    task_id = fields.Many2one('maintenance.request.task', 'Task request')
    wz_material_add_id = fields.Many2one('request.materials.additional', 'Wz materials additional')
    sequence = fields.Integer('Sequence', default=1)
    product_id = fields.Many2one('product.product', 'Product', required=True, check_company=True)
    product_qty = fields.Float('Quantity', default=1.0, digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    system_class_id = fields.Many2one(
        'maintenance.system.classification',
        domain=[('allocation_level', '=', True)],
        string='Component', ondelete='restrict',
        required=True)

    approval_request_id = fields.Many2one('approval.request', string='Approval Request', required=False)
    request_status = fields.Selection(related='approval_request_id.request_status')

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

    flag_approval = fields.Boolean(compute='_compute_flag_approval')

    @api.depends('task_id', 'wz_material_add_id')
    def _compute_flag_approval(self):
        for rec in self:
            flag_approval = False
            if rec.task_id and rec.wz_material_add_id:
                approval = rec.task_id.approval_ids.search([('wz_material_add_id', '=', rec.wz_material_add_id.id)],
                                                           limit=1)
                if approval:
                    flag_approval = approval.request_status == 'refused'
                    rec.sudo().approval_request_id = approval.id
            rec.sudo().flag_approval = flag_approval
