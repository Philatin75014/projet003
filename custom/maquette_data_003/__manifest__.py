{
    'name': 'Maquette003',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gestion des aiguillages',
    'depends': ['base','account','mail'],
    'data': [
        'views/my_model_view.xml',  
        'views/param_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}