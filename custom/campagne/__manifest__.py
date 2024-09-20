{
    'name': 'Offres',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gestion des offres',
    'depends': ['base','account','mail'],
    'data': [
        'views/campagne_views.xml',
        'views/synchro_wizard.xml',
        'views/export_buttons.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
