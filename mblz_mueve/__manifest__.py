# -*- coding: utf-8 -*-
{
    'name': "MBLZ: Mueve",

    'description': """
       Customizaciones Mueve by MBLZ
   """,
    'summary': 'Customizaciones Mueve by MBLZ',
    'website': "https://www.mobilize.cl",
    'category': 'Mobilize/Apps',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['helpdesk',
                'website_helpdesk_form',
                'helpdesk_timesheet',

                'fleet',
                'maintenance',
                'l10n_cl_maintenance',
                'mail',
                'purchase',
                'account',
                'project',
                'hr_timesheet',
                'product_code_unique',
                'report_xlsx',
                'html_text',
                'partner_vat_unique'
                ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/sequences.xml',

        'views/helpdesk_ticket.xml',
        'views/helpdesk_failure_level.xml',
        # 'views/helpdesk_support_activity.xml',
        'views/helpdesk_support_level.xml',
        'views/maintenance_request.xml',
        'views/res_users.xml',


        'data/helpdesk.failure.level.csv',

        'reports/helpdesk_ticket.xml',

        'views/template_helpdesk.xml',

        'views/settings.xml',
        # 'reports/monthly_tickets_pdf.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
        # 'reports/assets.xml',
        'reports/templates/ot_header.xml',
        'reports/templates/ot_body.xml',
        'reports/mtn_request_ot.xml',

        'reports/all/rpt_01.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

    'images': ['static/description/icon.png'],

    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
