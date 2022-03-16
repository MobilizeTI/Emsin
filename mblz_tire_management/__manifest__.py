# -*- coding: utf-8 -*-
{
    'name': "mblz: Tire Management",

    'summary': """
       ADMINISTRACIÓN DE LAS LLANTAS DE LA FLOTA DE MUEVE""",

    'description': """
    - CADA LLANTA INSTALADA O EN STOCK TIENE UN ID PARA EL CONTROL DE SU DESEMPEÑO Y VIDA ÚTIL
    - LAS ACTIVIDADES DE MANTENIMIENTO PREVENTIVO ESTÁN REGISTRADAS EN EL DOCUMENTO EXCEL DE PAUTAS DE MANTENIMIENTO, SISTEMA ALINEACIÓN Y LLANTAS
    - EL MANTENIMIENTO DE LAS LLANTAS SERÁ PLANEADO, EJECUTADO Y CONTROLADO POR PERSONAL DE MUEVE
    - SE INDICARÁN LAS PRESIONES, PROFUNDIDADES, KILOMETRAJE, ID CON SU RESPECTIVA UBICACIÓN PARA EL INICIO DE OPERACIÓN
    """,

    'author': "Mobilize",
    'website': "https://www.mobilize.cl",

    'version': '1.0',
    'category': 'Mobilize/Apps',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'fleet',
        # complements
        'web_notify', 'sh_message', 'report_xlsx', 'product_brand_inventory'
    ],

    # always loaded
    'data': [
        # ============================================================
        # SECURITY SETTING - GROUP - PROFILE
        # ============================================================
        # 'Security/',
        'security/security.xml',
        'security/ir.model.access.csv',

        # ============================================================
        # VIEWS OR WIZARD OR TEMPLATES
        # ============================================================
        # 'template/',
        # 'static/src/xml/action_manager.xml',

        # 'view/',
        'views/vehicle_rims.xml',

        # 'reports/',

        # 'wizards/',

        # 'templates/',

        # ============================================================
        #                           DATA
        # ============================================================
        # 'data/',

        # ============================================================
        # MENU
        # ============================================================
        # 'menu/',
        'menu/root.xml',
        'menu/menu1.xml'

        # ============================================================
        # DEMO
        # ============================================================
        # 'demo/',

        # ============================================================

        # ============================================================
        # FUNCTION USED TO UPDATE DATA LIKE POST OBJECT
        # ============================================================
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': True,
    'pre_init_hook': '',
    'post_init_hook': '',
    'uninstall_hook': '',
}
