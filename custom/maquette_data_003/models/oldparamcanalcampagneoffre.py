#from odoo import models, fields, api
from odoo import models, fields, api
from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_source_mpa_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_comites_data  
#from .prestataire_reference import PrestataireReference
#from .comite_reference import ComiteReference
class ParamCanalCampagneOffre(models.TransientModel):
 #class ParamCanalCampagneOffre(models.Model):
    _name = 'param.canal.campagne.offre'
    _description = 'Param Canal Campagne Offre'
     # Déclarer une variable de classe pour stocker les données chargées
     #_source_mpa_data_cache = None

    type_canal = fields.Char(string='Type Canal')
    type_canal_label = fields.Char(string='Canal Acquisition', compute='_compute_type_canal_label')    
    code_source = fields.Char(string='Code Source')
    code_source_id = fields.Many2one('prestataire.reference', string='Prestataire Reference', compute='_compute_code_source_id', store=True)
    code_source_label = fields.Char(string='Source', related='code_source_id.libelle_source')    
    code_comite = fields.Char(string='Code Comité')
    libelle_operation = fields.Char(string='Libellé Opération')
    code_operation_campagne = fields.Char(string='Code Opération Campagne')
    code_mission_offre = fields.Char(string='Code Mission Offre')
    code_campagne = fields.Char(string='Code Campagne')
    code_offre = fields.Char(string='Code Offre')
    date_debut_ope = fields.Date(string='Date Début Opération')
    date_fin_ope = fields.Date(string='Date Fin Opération')

  
    @api.depends('type_canal')
    def _compute_type_canal_label(self):
        for record in self:
            if record.type_canal == 'PAS':
                record.type_canal_label = 'PA STREET'
            else:
                record.type_canal_label = record.type_canal  # Si aucune correspondance, afficher la valeur brute

    @api.depends('code_source')
    def _compute_code_source_id(self):
        """ Logique pour remplir le champ code_source_id en fonction de code_source """
        for record in self:
            # Initialiser reference à False par défaut
            reference = False
            if record.code_source:
            # Chercher la référence dans la table prestataire.reference
                reference = self.env['prestataire.reference'].search([('code_source', '=', record.code_source)], limit=1)
            if reference:
                record.code_source_id = reference  # Assigner la référence trouvée
            else:
                record.code_source_id = False  # Aucune référence trouvée, assigner False
        else:
            # Si 'code_source' est vide ou inexistant, assigner False
            record.code_source_id = False


    @api.model
    def load_data_from_sql(self, code_comite):
        # Charger les données de référence avant de charger les données principales
        # Charger les données de référence depuis le modèle PrestataireReference
        # Importation différée pour éviter les importations circulaires
        prestataire_model = self.env['prestataire.reference']
        comite_model = self.env['comite.reference']

        # Charger les données de référence avant de charger les données principales
        prestataire_model.load_prestataire_reference()
        comite_model.load_comite_reference()

        #self.env['prestataire.reference'].load_prestataire_reference()
        #self.env['comite.reference'].load_comite_reference()

        # Exécuter ta fonction SQLAlchemy et récupérer les données
        records = get_param_canal_campagne_offre_data(code_comite)
        
        # Créer des enregistrements dans le modèle à partir des données retournées
        for record in records:
            self.create({
                'type_canal': record.get('TYPE_CANAL'),
                'code_source': record.get('CODE_SOURCE'),
                'code_comite': record.get('CODE_COMITE'),
                'libelle_operation': record.get('LIBELLE_OPERATION'),
                'code_operation_campagne': record.get('CODE_OPERATION_CAMPAGNE'),
                'code_mission_offre': record.get('CODE_MISSION_OFFRE'),
                'code_campagne': record.get('CODE_CAMPAGNE'),
                'code_offre': record.get('CODE_OFFRE'),
                'date_debut_ope': record.get('DATE_DEBUT_OPE'),
                'date_fin_ope': record.get('DATE_FIN_OPE'),
            })
               
                

    @api.model
    
    #def search(self, args, offset=0, limit=None, order=None, count=False):
        # Charger les données avant la recherche
        #self.load_data_from_sql('044')  # Remplace '001' par ton paramètre dynamique si nécessaire
        #return super(ParamCanalCampagneOffre, self).search(args, offset=offset, limit=limit, order=order, count=count)
    
    def manual_reload_data(self,context=None):
        """
        Méthode appelée lorsqu'on clique sur le bouton "Charger Données".
        """
        """Purge les enregistrements existants et recharge les nouveaux"""
     
        # Étape 1 : Rechercher les enregistrements existants
        existing_records = self.search([])

        # S'assurer qu'il y a bien des enregistrements à supprimer avant de les purger
        if existing_records:
            existing_records.unlink()
        # Étape 2 : Recharger les nouvelles données depuis SQL Server            
            self.load_data_from_sql('000')  # Recharge manuellement les données depuis SQL
        # Étape 2 : Recharger les nouvelles données depuis SQL Server            
        #    ComiteReference.load_comite_reference()   # Recharge manuellement les données depuis SQL

    # # Étape 4 : Retourner une action 'act_window' pour forcer un rechargement complet de la vue
        return {
        'type': 'ir.actions.act_window',
        'name': 'Param Canal Campagne Offres',
        'res_model': 'param.canal.campagne.offre',
        'view_mode': 'tree',
        'target': 'current',
                }
  