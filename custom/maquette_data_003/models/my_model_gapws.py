from odoo import models, fields

class MyModelGapws(models.Model):
    _name = 'model.gapws'
    _description = 'My Model Gapws'

    name = fields.Char(string='Name')
    value = fields.Integer(string='Value')