{
    'name': 'PetStyle',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Manage pets and bath orders',
    'depends': ['base'],
    'data': [
        'security/petstyle_security.xml',
        'security/ir.model.access.csv',
        'views/pet_views.xml',
        'views/bath_order_views.xml',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/petstyle_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
