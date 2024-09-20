{
    'name': 'toto',
    'version': '1.0',
    'summary': 'Module personnalisé',
    'description': 'Description de Maquette002',
    'category': 'Tools',
     'author': 'Philippe Amary',
    'depends': ['base'],
    'data': [
        'views/my_model_view.xml',  
        'security/ir.model.access.csv', 
    ],
    'installable': True,
    'application': False,
}