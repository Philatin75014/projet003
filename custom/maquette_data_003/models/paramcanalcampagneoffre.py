from odoo import models, fields, api, exceptions
from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
from .utils.datasource import get_source_list_offre_potentielles  # Import depuis le sous-répertoire

class ParamCanalCampagneOffre(models.TransientModel):
    _name = 'param.canal.campagne.offre'
    _description = 'Param Canal Campagne Offre'

   # Un dictionnaire pour stocker temporairement des valeurs
    #session_store = {}
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
    #libelle_total_mission_offre = fields.Char(string="Mission Offre")  # Nouveau champ
    libelle_total_mission_offre = fields.Selection([], string="Mission Offre")  # Champ liste déroulante avec une liste vide par défaut


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
    
        
    # Méthode pour obtenir les comités sous forme de liste déroulante
    @api.model
    def _get_comites(self):
        comites = self.env['comite.reference'].search([])
        return [(comite.code_comite, comite.nom) for comite in comites]


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
    
    #def Get_dico_offres_potentielles(self,code_comite):
        # Récupérer les offres potentielles

    #    offres_potentielles = self.env['param.canal.campagne.offre'].search([])
    #    return offres_potentielles
    

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
                
    @api.onchange('comite_selection')
    def _onchange_comite_selection(self):
      if self.comite_selection:
       # Extraire le code_comite à partir de la sélection
            code_comite_selection = self.comite_selection.split(' ')[0]
            # Appeler la méthode pour récupérer le dictionnaire des offres potentielles
            offres_potentielles = get_source_list_offre_potentielles(code_comite_selection)
            print(f"Offres potentielles récupérées : {offres_potentielles}")
            if offres_potentielles:
            # Créer une liste d'options pour remplir la liste déroulante
             options = [
                (f"{offre.get('code_campagne')}_{offre.get('code_mission_offre')}_{offre.get('libelle_off')}", offre.get('libelle_total'))  # Clé unique = code_campagne + code_offre
                for offre in offres_potentielles
            ]
              # Mettre à jour les options du champ de sélection
             self._fields['libelle_total_mission_offre'].selection = options
             self.libelle_total_mission_offre = options[0][0] if options else False  # Prend la clé de la première option
             #  Mettre à jour la liste déroulante et stocker les offres dans un dictionnaire de session
             """"
             self.libelle_total_mission_offre = options[0][0] if options else False  # Prend la clé de la première option
            # Stocker les informations supplémentaires dans le dictionnaire de session
             self.session_store = {
                offre['libelle_total']: {
                    'code_campagne': offre.get('code_campagne'),
                    'code_mission_offre': offre.get('code_mission_offre'),
                    'libelle_off': offre.get('libelle_off'),  # LIBELLE_OFF si nécessaire
                    'autre_champ': offre.get('autre_champ')  # Ajouter tous les champs supplémentaires que vous voulez
                } 
                for offre in offres_potentielles
            }"""
            else:
                # Réinitialiser si aucune offre trouvée
                self.libelle_total_mission_offre = False
                self.session_store = {}
      else:
          # Réinitialiser tout si aucun comité sélectionné
            self.libelle_total_mission_offre = False
            self.session_store = {}

@api.onchange('libelle_total_mission_offre')
def _onchange_libelle_total_mission_offre(self):
    if self.libelle_total_mission_offre:
        # Extraire les composants de la valeur sélectionnée
        parts = self.libelle_total_mission_offre.split('_')  # Exemple : "code_campagne_code_mission_offre_libelle_off"
        if len(parts) == 3:  # Vérifie que nous avons bien 3 éléments
            code_campagne_selectionnee = parts[0]
            code_mission_offre_selectionnee = parts[1]
            libelle_off_selectionne = parts[2]

            # Mettre à jour les champs correspondants
            self.code_campagne = code_campagne_selectionnee
            self.code_mission_offre = code_mission_offre_selectionnee
            self.libelle_operation = libelle_off_selectionne  # Utiliser libelle_off

            print(f"Offre sélectionnée : Code Campagne - {self.code_campagne}, Code Mission Offre - {self.code_mission_offre}, Libellé - {self.libelle_operation}")
        else:
            print("Format incorrect pour libelle_total_mission_offre.")
    else:
        # Réinitialiser les champs si aucune offre n'est sélectionnée
        self.code_campagne = ''
        self.code_mission_offre = ''
        self.libelle_operation = ''
        print("Aucune offre sélectionnée.")