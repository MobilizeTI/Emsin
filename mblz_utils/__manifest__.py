# -*- coding: utf-8 -*-
{
    'name': "MBLZ: Utils",

    'summary': """
        Módulo con utilidades comunes en todos los proyectos
       """,

    'description': """
        Módulo con utilidades comunes en todos los proyectos
    """,
    "category": "Mobilize/Tools",

    'author': 'Mobilize (Cristobal OCH)',
    'website': "https://www.mobilize.cl",

    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
    ],
    "qweb": ["templates/web_page_button_refresher.xml"],

}
