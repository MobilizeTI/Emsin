# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Maintenance Request Stage transition",
    "summary": """
        Manage transition visibility and management between stages""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/maintenance",
    'category': 'Mobilize/Apps',
    "depends": [
        "maintenance",
        'l10n_cl_maintenance',
        'mblz_utils'
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/maintenance_request.xml",
        "views/maintenance_stage.xml",
        "wizard/stage_motive_wizard.xml"
    ],

    # "demo": ["data/demo_maintenance_request_stage_transition.xml"],

    "maintainers": ["etobella"],
}
