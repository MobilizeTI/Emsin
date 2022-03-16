# -*- encoding: utf-8 -*-
{
    'name': 'MBLZ: Chile - Maintenance MRP',
    'version': '1.0',
    'category': 'Mobilize/Apps',
    'summary': 'Programe y gestione el mantenimiento de máquinas y herramientas.',
    'website': "https://www.mobilize.cl",

    'description': """
        Solicitar lista de materiales para un mantenimiento ...
    """,

    'depends': ['mrp_maintenance', 'l10n_cl_maintenance', 'approvals', 'web_notify'],
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_data.xml',
        'data/approval_request_categ.xml',
        'data/cron.xml',

        'views/maintenance_stage.xml',
        'views/maintenance_guideline.xml',

        'views/maintenance_request.xml',

        'views/maintenance_team.xml',
        'views/maintenance_equipment.xml',

        'wizard/select_multiple_product.xml',
        'wizard/request_materials_additional.xml',

        'views/mrp_bom.xml',
        'views/stock_picking.xml',
        'views/maintenance_request_task.xml',
        'views/approval_request.xml',
    ],
    # 'demo': ['data/mrp_maintenance_demo.xml'],
    'images': ['static/description/icon.png'],

    'installable': True,
    'auto_install': True,
    'application': True,
    'license': 'AGPL-3',
}
# Part of Odoo. See LICENSE file for full copyright and licensing details.
