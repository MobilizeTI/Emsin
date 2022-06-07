# -*- coding: utf-8 -*-
{
    'name': "EMSIN - Customizaciones",

    'summary': """
        Customizaciones EMSIN.""",

    'description': """
        Customizaciones EMSIN.
    """,

    'author': "Mobilize Spa.",
    'website': "http://mobilize.cl",
    'contribuitors': "Felipe Angulo <felipe@mobilize.cl>",
    'version': '0.1',
    'images': ['static/description/icon.png'],

    'depends': [
        'sale',
        'l10n_cl',
        'account'
    ],

    'data': [
        'views/sale_advance_payment_inv_views.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'auto_install': True,
    'demo': [],
    'test': [],
}