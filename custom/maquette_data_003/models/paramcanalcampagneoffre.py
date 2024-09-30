from odoo import models, fields, api

class ParamCanalCampagneOffre(models.TransientModel):
    _name = 'param.canal.campagne.offre'
    _description = 'Param Canal Campagne Offre'

    # Champs
    type_canal = fields.Char(string='Type Canal')
    type_canal_label = fields.Char(string='Canal Acquisition', compute='_compute_type_canal_label')    
    code_source = fields.Selection(selection='_get_prestataires', string='Code Source')  # Liste déroulante basée sur prestataire.reference
    code_source_label = fields.Char(string='Source', compute='_compute_code_source_label')

    code_comite = fields.Selection(selection='_get_comites', string='Comité')
    # code_campagne = fields.Selection(selection='_get_campagnes', string='Code Campagne')  # À activer une fois disponible
    
    libelle_operation = fields.Char(string='Libellé Opération')
    code_operation_campagne = fields.Char(string='Code Opération Campagne')
    code_mission_offre = fields.Char(string='Code Mission Offre')
    code_offre = fields.Char(string='Code Offre')
    date_debut_ope = fields.Date(string='Date Début Opération')
    date_fin_ope = fields.Date(string='Date Fin Opération')

    # Méthode pour obtenir les prestataires sous forme de liste déroulante
    @api.model
    def _get_prestataires(self):
        prestataires = self.env['prestataire.reference'].search([])
        return [(prestataire.code_source, prestataire.libelle_source) for prestataire in prestataires]

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
        if 'code_source' in vals:
            prestataire_exists = self.env['prestataire.reference'].search([('code_source', '=', vals['code_source'])], limit=1)
            if not prestataire_exists:
                raise ValueError("Le code source sélectionné n'existe pas.")

        if 'code_comite' in vals:
            comite_exists = self.env['comite.reference'].search([('code_comite', '=', vals['code_comite'])], limit=1)
            if not comite_exists:
                raise ValueError("Le comité sélectionné n'existe pas.")
        
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
