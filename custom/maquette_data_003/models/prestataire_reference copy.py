#from odoo import models, fields, api
from odoo import models, fields, api
#from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
from .utils.datasource import get_source_mpa_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_comites_data  
    
class PrestataireReference(models.TransientModel):
        _name = 'prestataire.reference'
        _description = 'Prestataire Reference'
    
        code_source = fields.Char(string='Code Source', required=True)
        libelle_source = fields.Char(string='Libellé Source', required=True)
    
        @api.model
        def load_prestataire_reference(self):
            # Charger les données de la table SQL
            source_mpa_data = get_source_mpa_data()
    
            # Parcourir les données et créer des enregistrements dans prestataire.reference
            for item in source_mpa_data:
                # Vérifier si le code_source existe déjà
                existing_reference = self.env['prestataire.reference'].search([('code_source', '=', item['CODE_SOURCE'])], limit=1)
            
                if not existing_reference:
                    # Créer un nouvel enregistrement si le code_source n'existe pas
                    self.env['prestataire.reference'].create({
                        'code_source': item['CODE_SOURCE'],
                        'libelle_source': item['LIBELLE_SOURCE'],
                    })
                    
