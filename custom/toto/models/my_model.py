from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'

    name = fields.Char('Name')
    description = fields.Text('Description')  # Ajout du champ description
