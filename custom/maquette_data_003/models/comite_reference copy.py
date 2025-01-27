#from odoo import models, fields, api
from odoo import models, fields, api
#from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_source_mpa_data  # Import depuis le sous-répertoire
from .utils.datasource import get_comites_data  
    
class ComiteReference(models.Model):
    _name = 'comite.reference'
    _description = 'Comite Reference'

    code_comite = fields.Char(string='CODE_COMITE', required=True)
    nom = fields.Char(string='NOM', required=True)
    cible = fields.Char(string='CIBLE', required=True)
    date_migration_donalig = fields.Char(string='DATE_MIGRATION_DONALIG', required=True)    
    @api.model
    def load_comite_reference(self):
        # Charger les données de la table SQL
        comites_data = get_comites_data()
        
        # Créer un dictionnaire pour réutiliser les infos plus facilement
        comites_dict = {}

        # Parcourir les données et créer des enregistrements dans comite.reference
        for item in comites_data:
            # Vérifier si le code_comite existe déjà
            existing_reference = self.env['comite.reference'].search([('code_comite', '=', item['CODE_COMITE'])], limit=1)

            if not existing_reference:
                # Créer un nouvel enregistrement si le code_comite n'existe pas
                new_record = self.create({
                    'code_comite': item.get('CODE_COMITE'),
                    'nom': item.get('NOM'),
                    'cible': item.get('CIBLE'),
                    'date_migration_donalig': item.get('DATE_MIGRATION_DONALIG'),
                })
                
                # Ajouter les infos au dictionnaire, y compris le champ combiné code_comite_nom
                comites_dict[item.get('CODE_COMITE')] = {
                    'code_comite_nom': f"{item.get('CODE_COMITE')} {item.get('NOM')}",
                    'nom': item.get('NOM'),
                    'cible': item.get('CIBLE'),
                    'date_migration_donalig': item.get('DATE_MIGRATION_DONALIG'),
                }
                print(f"CODE_COMITE: {item.get('CODE_COMITE')}, NOM: {item.get('NOM')}")

        
        # Le dictionnaire 'comites_dict' contient maintenant toutes les informations, y compris 'code_comite_nom'
        return comites_dict
