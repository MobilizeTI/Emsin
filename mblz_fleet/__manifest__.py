# -*- coding: utf-8 -*-
{
    'name': "MBLZ: Flota",

    'summary': """
       Customizaciones modulo de flota""",

    'description': """
        1.- Registro de combustible
    """,

    'author': "Mobilize",
    'website': "https://www.mobilize.cl",

    'version': '1.0',
    'category': 'Mobilize/Apps',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'uom', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fuel_tank.xml',
        'views/vehicle_fuel_log.xml',
        'views/fleet_vehicle.xml',
        'views/fleet_vehicle_odometer.xml',
        'views/res_config_settings.xml',

        'wizard/add_liters.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
