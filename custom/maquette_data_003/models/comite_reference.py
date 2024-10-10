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
        # Champ combiné code_comite_nom
    code_comite_nom = fields.Char(string='CODE_COMITE_NOM')   
    @api.model
    def load_comite_reference(self):
        # Charger les données de la table SQL
        comites_data = get_comites_data()

        # Vérifier que les données sont récupérées
        if not comites_data:
            return  # Ne rien faire si aucune donnée n'est récupérée

        # Parcourir les données et recréer tous les enregistrements
        for item in comites_data:
        # Création de l'enregistrement avec code_comite_nom
         self.create({
            'code_comite': item.get('CODE_COMITE'),
            'nom': item.get('NOM'),
            'code_comite_nom': item.get('CODE_COMITE_NOM'),
            'cible': item.get('CIBLE'),
            'date_migration_donalig': item.get('DATE_MIGRATION_DONALIG'),
        })

        # Retourner directement comites_data pour une réutilisation ultérieure
        #print("Vérification finale de comites_data avec code_comite_nom:", comites_data)
        return comites_data
