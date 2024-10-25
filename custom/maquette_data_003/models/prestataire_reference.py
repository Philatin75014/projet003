#from odoo import models, fields, api
from odoo import models, fields, api
#from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
from .utils.datasource import get_source_mpa_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_comites_data  
    
class PrestataireReference(models.TransientModel):
        _name = 'prestataire.reference'
        _description = 'Prestataire Reference'
        _rec_name='libelle_source'  

    
        code_source = fields.Char(string='Code Source', required=True,unique=True)
        libelle_source = fields.Char(string='Libellé Source', required=True)
    
    # Définir le champ name pour l'affichage dans le Many2one
        def name_get(self):
         result = []
         for record in self:
            name = f"{record.code_source} - {record.libelle_source}"  # Personnaliser le format affiché
            result.append((record.id, name))
         return result

        @api.model
        def load_prestataire_reference(self):
            # Charger les données de la table SQL
            source_mpa_data = get_source_mpa_data()

            # Vérifiez que les données sont récupérées
            if not source_mpa_data:
                return  # Ne rien faire si aucune donnée n'est récupérée

            # Créer un dictionnaire à partir des données source pour un accès rapide
            source_data_dict = {item['CODE_SOURCE']: item['LIBELLE_SOURCE'] for item in source_mpa_data}

            # Récupérer tous les enregistrements existants
            existing_references = self.env['prestataire.reference'].search([])

            # Mettre à jour ou supprimer des enregistrements existants
            for reference in existing_references:
                if reference.code_source in source_data_dict:
                    # Mettre à jour l'enregistrement si le code_source existe dans la source
                    reference.libelle_source = source_data_dict[reference.code_source]
                else:
                    # Supprimer l'enregistrement s'il n'est plus dans la source
                    reference.unlink()

            # Créer des enregistrements pour les nouveaux codes_source
            for code_source, libelle_source in source_data_dict.items():
                if not self.env['prestataire.reference'].search([('code_source', '=', code_source)]):
                    self.env['prestataire.reference'].create({
                        'code_source': code_source,
                        'libelle_source': libelle_source,
                        })