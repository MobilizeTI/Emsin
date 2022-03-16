# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RequestMaterialsAdditional(models.Model):
    _name = 'request.materials.additional'
    _description = 'Request Materials Additional'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)

    # Lista de materiales adicionales
    task_id = fields.Many2one('maintenance.request.task', string='Task', required=False)
    product_line_ids = fields.One2many('task.line.materials',
                                       'wz_material_add_id', 'Product Lines', copy=True)

    approval_reason = fields.Text(string='Approval reason', required=True)

    def action_create(self):
        if len(self.product_line_ids) > 0:
            approval_request = self.env['approval.request'].sudo()

            # category_id = self.env.ref('l10n_cl_mrp_maintenance.approval_request_task').id
            category_id = self.env['approval.category'].sudo().search(
                [('sequence_code', '=', 'RMA'), ('company_id', '=', self.company_id.id)],
                limit=1)
            if not category_id:
                raise ValidationError(
                    f'No exíste la categoría de aprovación Materiales Adicionales (MTM) con código RMA para la companía {self.company_id.name}')
            current_date = fields.Datetime.now()
            partner_id = self.task_id.user_id.partner_id.id
            name_seq = self.task_id.name_seq
            if not name_seq:
                name_seq = f"({self.task_id.name.split('(')[1]}"
            else:
                name_seq = f'({self.task_id.name_seq})'

            approval_vals = {
                'name': f'Aprobación de solicitud {name_seq}',
                'category_id': category_id.id,
                'date': current_date,
                'partner_id': partner_id,
                'request_task_id': self.task_id.id,
                'wz_material_add_id': self.id,
                'reason': self.approval_reason,
                'company_id': self.company_id.id,
            }
            approval_request_new = approval_request.create(approval_vals)
            approval_request_new.sudo()._onchange_category_id()
            approval_request_new.sudo().action_confirm()
            self.sudo().task_id.approval_ids = [(4, approval_request_new.id)]
            # self.state_approval = 'to approve'
            return True
        else:
            raise ValidationError(_('Material requested list empty!'))
