from odoo import models, fields, api, exceptions
from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire

class ParamCanalCampagneOffre(models.TransientModel):
    _name = 'param.canal.campagne.offre'
    _description = 'Param Canal Campagne Offre'

    # Champs
    type_canal = fields.Char(string='Type Canal')
    type_canal_label = fields.Char(string="Canal d'acquisition", compute='_compute_type_canal_label')    
    #code_source = fields.Selection(selection='_get_prestataires', string='Code Source')  # Liste déroulante basée sur prestataire.reference
    #code_source_label = fields.Char(string='Source', compute='_compute_code_source_label')

    #code_source = fields.Char(string='Code Source')  # Liste déroulante basée sur prestataire.reference
    #code_source_label = fields.Char(string='Source', compute='_compute_code_source_label')
    code_source = fields.Selection(selection='_get_prestataires', string='Code Source', required=True)
    #code_source = fields.Many2one('prestataire.reference', string="Code Source")
    #code_source_label = fields.Char(string="Source", compute="_compute_code_source_label", store=True)

    #code_comite = fields.Selection(selection='_get_comites', string='Comité')
    #code_campagne = fields.Selection(selection='_get_campagnes', string='Code Campagne')  # À activer une fois disponible
    # Champ de sélection basé sur le dictionnaire combinant code_comite et nom
    comite_selection = fields.Selection(selection='_get_comite_selection',string="Comité")
    code_comite = fields.Char(string='Comité')
    code_campagne = fields.Char(string='Code Campagne') 
    
    libelle_operation = fields.Char(string='Libellé Opération')
    code_operation_campagne = fields.Char(string='Code Opération Campagne')
    code_mission_offre = fields.Char(string='Code Mission Offre')
    #code_offre = fields.Char(string='Code Offre')
    date_debut_ope = fields.Date(string='Date Début Opération', required=True)
    date_fin_ope = fields.Date(string='Date Fin Opération', required=True)

    @api.model
    def load_data_from_sql(self, code_comite):
        # Charger les données de référence avant de charger les données principales
        # Charger les données de référence depuis le modèle PrestataireReference
        # Importation différée pour éviter les importations circulaires
        self.env['prestataire.reference'].load_prestataire_reference()
        self.env['comite.reference'].load_comite_reference()
        
        # Exécuter ta fonction SQLAlchemy et récupérer les données
        records = get_param_canal_campagne_offre_data(code_comite)
        
        # Créer des enregistrements dans le modèle à partir des données retournées
        for record in records:
            prestataire = self.env['prestataire.reference'].search([('code_source', '=', record.get('CODE_SOURCE'))], limit=1)
            if prestataire:
             self.create({
                'type_canal': record.get('TYPE_CANAL'),
                #'code_source': prestataire.id, #record.get('CODE_SOURCE'),
                'code_source':record.get('CODE_SOURCE'),
                'code_comite': record.get('CODE_COMITE'),
                'comite_selection': record.get('CODE_COMITE'),
                'libelle_operation': record.get('LIBELLE_OPERATION'),
                'code_operation_campagne': record.get('CODE_OPERATION_CAMPAGNE'),
                'code_mission_offre': record.get('CODE_MISSION_OFFRE'),
                'code_campagne': record.get('CODE_CAMPAGNE'),
                #'code_offre': record.get('CODE_OFFRE'),
                'date_debut_ope': record.get('DATE_DEBUT_OPE'),
                'date_fin_ope': record.get('DATE_FIN_OPE'),
            })
            else:
             raise ValueError("Le code source {} n'existe pas dans les données de référence.".format(record.get('CODE_SOURCE')))
     # Méthode pour obtenir les prestataires sous forme de liste déroulante
    @api.model
    def _get_prestataires(self):
        prestataires = self.env['prestataire.reference'].search([])
        return [(prestataire.code_source, prestataire.libelle_source) for prestataire in prestataires]
    
    def _get_comite_selection(self):
        # Charger le dictionnaire avec les comités et leurs noms combinés

        comites = self.env['comite.reference'].search([])
        return [(comite.code_comite, comite.code_comite_nom) for comite in comites]
    
        #comites_data = self.env['comite.reference'].load_comite_reference()
        #print(comites_data)  # Vérification du contenu du dictionnaire
        
        # Créer une liste de tuples pour la liste déroulante (Selection)
        # Parcourir la liste de dictionnaires pour créer les tuples
        #return [(item['CODE_COMITE'], item['code_comite_nom']) for item in comites_data]
        # Créer une liste de tuples pour la liste déroulante (Selection)
        #return [(code_comite, data['code_comite_nom']) for code_comite, data in comites_data.items()]   

    # Méthode pour obtenir les comités sous forme de liste déroulante
    @api.model
    def _get_comites(self):
        comites = self.env['comite.reference'].search([])
        return [(comite.code_comite, comite.nom) for comite in comites]

    # Méthode pour obtenir les campagnes sous forme de liste déroulante (commentée en attendant la création du modèle)
    # @api.model
    # def _get_campagnes(self):
    #     campagnes = self.env['campagne.reference'].search([])
    #     return [(campagne.code_campagne, campagne.name) for campagne in campagnes]
    """
    @api.onchange('code_source')
    def _onchange_code_source(self):
        if self.code_source:
            self.code_source_label = self.code_source.libelle_source
    """

    @api.depends('code_source')
    def _compute_code_source_label(self):
        """Calcul du libellé de la source en fonction du code source sélectionné."""
        for record in self:
            if record.code_source:
                prestataire = self.env['prestataire.reference'].search([('code_source', '=', record.code_source)], limit=1)
                record.code_source_label = prestataire.libelle_source if prestataire else ''
            else:
                record.code_source_label = 'Code source non défini'

    @api.depends('type_canal')
    def _compute_type_canal_label(self):
        """Calcul du libellé du canal en fonction du type de canal sélectionné."""
        for record in self:
            if record.type_canal == 'PAS':
                record.type_canal_label = 'PA STREET'
            else:
                record.type_canal_label = record.type_canal  # Si aucune correspondance, afficher la valeur brute

    @api.model
    def create(self, vals):
        """Méthode pour vérifier que les valeurs sélectionnées existent déjà dans les tables liées lors de la création."""
        """
                         if 'code_source' in vals:
            prestataire_exists = self.env['prestataire.reference'].search([('code_source', '=', vals['code_source'])], limit=1)
            if not prestataire_exists:
                raise ValueError("Le code source sélectionné n'existe pas.")

        if 'code_comite' in vals:
            comite_exists = self.env['comite.reference'].search([('code_comite', '=', vals['code_comite'])], limit=1)
            if not comite_exists:
                raise ValueError("Le comité sélectionné n'existe pas.")
      """
        return super(ParamCanalCampagneOffre, self).create(vals)

    def manual_reload_data(self):
        """Méthode pour recharger les données manuellement."""
        existing_records = self.search([])
        if existing_records:
            existing_records.unlink()
        self.load_data_from_sql('000')  # Exemple de rechargement manuel
        return {
            'type': 'ir.actions.act_window',
            'name': 'Param Canal Campagne Offres',
            'res_model': 'param.canal.campagne.offre',
            'view_mode': 'tree',
            'target': 'current',
        }

    @api.model
    def load_data_on_start(self):
        """ Charger les données lors de l'accès à la vue """
        self.manual_reload_data()
    
    @api.constrains('date_debut_ope', 'date_fin_ope')
    def _check_dates(self):
        for record in self:
            if record.date_debut_ope and record.date_fin_ope:
                if record.date_debut_ope > record.date_fin_ope:
                    raise exceptions.ValidationError(
                        "La date de début de l'opération ne peut pas être plus récente que la date de fin."
                    )
                
                