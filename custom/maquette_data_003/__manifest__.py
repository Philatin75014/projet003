{
    'name': 'Maquette003',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gestion des aiguillages',
    'depends': ['base','account','mail'],
    'data': [
        'views/param_view.xml',
        'views/prestataire_reference_view.xml',
        'views/comite_reference_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
