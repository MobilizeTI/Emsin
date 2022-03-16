# -*- coding: utf-8 -*-

{
    'name': 'MBLZ: Chile - Maintenance',
    'version': '1.0',
    'sequence': 125,
    'category': 'Mobilize/Apps',
    'description': """
        Seguimiento de los equipos y de las solicitudes de mantenimiento
    """,
    'summary': 'Seguimiento de los equipos y gestión de las solicitudes de mantenimiento',
    'website': "https://www.mobilize.cl",
    'depends': [
        'maintenance',
        'uom',
        'mail',
        'timer',
        # 'hr',
        'hr_timesheet',
        'account',

        'stock',
        'fleet',
        'mblz_utils',
        'sh_message',
        'maintenance_equipment_hierarchy',
        'web_notify',
        'mblz_access_control'
    ],

    'data': [
        # 'security/maintenance.xml',
        'security/security.xml',
        'security/security_mueve.xml',
        'security/ir.model.access.csv',

        'data/ir.model.access.csv',
        'data/sequences.xml',
        'data/email_demo.xml',

        # 'data/maintenance_data.xml',
        # 'data/mail_data.xml',
        'views/hr_speciality_tag.xml',
        'views/maintenance_system.xml',
        'views/system_classification.xml',
        'views/guideline_activity.xml',
        'views/hr_employee.xml',

        'wizard/select_all_activities_view.xml',
        'views/maintenance_guideline.xml',
        'views/maintenance_equipment.xml',
        'views/equipment_odometer_log.xml',

        'views/maintenance_request.xml',
        'views/maintenance_request_master.xml',
        'views/maintenance_request_type.xml',
        'views/request_task_stage.xml',
        'views/maintenance_request_task.xml',
        'views/ot_template_view.xml',
        'views/maintenance_motive_stage.xml',

        # fleet
        'views/fleet/fleet_vehicle.xml',

        # wizard
        'wizard/guideline_line_confirm.xml',
        'wizard/request_task_create_timesheet.xml',
        'wizard/request_task_stage_delete.xml',
        'wizard/scheduler_ot_new_views.xml',
        'wizard/mtm_request_task_update_wz.xml',

        # menu
        'menus/guideline_menu.xml',
        'menus/tasks_menu.xml',
        'menus/system_classification_menu.xml',

        # 'views/maintenance_templates.xml',
        # 'views/mail_activity_views.xml',

        # 'data/maintenance_cron.xml',
        'data/ot_cron.xml',
        'data/request_task_stage.xml',
        # 'data/delete_rules.xml',
        'data/maintenance.request.type.csv',

    ],
    'demo': [],
    'images': ['static/description/icon.png'],

    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
