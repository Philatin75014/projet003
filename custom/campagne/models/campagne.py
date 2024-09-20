from odoo import models, fields, api
from odoo.exceptions import ValidationError
import os
from simple_salesforce import Salesforce
from .utils import sf_api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    sf__id = fields.Char("Id sf",readonly=True)
    count_occurrence = fields.Integer("# occurrences",readonly=True)
    duplicate = fields.Boolean(string='Plusieurs occurrences', compute='_compute_duplicate')

    @api.depends('count_occurrence')
    def _compute_duplicate(self):
        for record in self:
            record.duplicate = record.count_occurrence > 1

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _default_plan_id(self):
        plan_record = self.env['account.analytic.plan'].search([('name', '=', 'LNCC')], limit=1)
        if not plan_record:
            plan_record = self.env['account.analytic.plan'].create({'name': 'LNCC'})
        return plan_record.id
    
    @api.depends('count_occurrence')
    def _compute_duplicate(self):
        for record in self:
            record.duplicate = record.count_occurrence > 1

    count_occurrence = fields.Integer("# occurrences",readonly=True)
    duplicate = fields.Boolean(string='Plusieurs occurrences', compute='_compute_duplicate')
    plan_id = fields.Many2one('account.analytic.plan', default=_default_plan_id)
    type = fields.Selection([
        ('axe_1', 'Axe 1'),
        ('axe_2_3', 'Axe 2/3')
    ], string='Type')
    sf__id = fields.Char("Id sf",readonly=True)

class ExportOps(models.Model):
    _name = 'export.ops'
    _description = 'Export ops'

    model_id = fields.Integer(string="Id",readonly=True)
    model_name = fields.Char(string="Model", readonly=True)
    mode = fields.Selection([
        ('test', 'PreProd'),
        ('prod', 'Prod')
    ], string='Mode',readonly=True)
    operation = fields.Selection([
        ('insert', 'Création'),
        ('update', 'MAJ')
    ], string='Opération',readonly=True)  
    #all
    name = fields.Boolean("Nom",readonly=True)
    code = fields.Boolean("Code",readonly=True)
    date_start = fields.Boolean("Date de début",readonly=True)
    date_end = fields.Boolean("Date de fin",readonly=True)
    siege = fields.Boolean("Origine",readonly=True)
    comites = fields.Boolean("Comites",readonly=True)
    #campagne
    cible = fields.Boolean("Cible",readonly=True)
    canal = fields.Boolean("Canal",readonly=True)
    creation_comites = fields.Boolean("Création comités",readonly=True)
    #Offre
    levier = fields.Boolean("Levier",readonly=True)
    accounts = fields.Boolean("Comptes et axes comptables",readonly=True)
    campagne = fields.Boolean("Campagne",readonly=True)
    done = fields.Boolean("Export effectué",readonly=True)

class LogLine(models.Model):
    _name = 'campagne.log.line'
    _description = 'log line'

    name = fields.Char("Code",readonly=True)
    sf__id = fields.Char("Id (sf)",readonly=True)
    log_id = fields.Many2one("campagne.log",string="Log",readonly=True)

class Log(models.Model):
    _name = 'campagne.log'
    _description = 'log'

    name = fields.Char("Nom",readonly=True)
    line_ids = fields.One2many('campagne.log.line', 'log_id', string="Lignes",readonly=True)

class Comite(models.Model):
    _name = 'campagne.comite'
    _description = 'Comité'

    name = fields.Char("Nom",required=True)

class ComiteSysmarlig(models.Model):
    _name = 'campagne.comite.sysmarlig'
    _description = 'Comité sysmarlig'

    name = fields.Char("Nom",required=True)

class Cible(models.Model):
    _name = 'campagne.cible'
    _description = 'Cible'

    name = fields.Char("Nom",required=True)

class Canal(models.Model):
    _name = 'campagne.canal'
    _description = 'Canal'

    name = fields.Char("Nom",required=True)

class Levier(models.Model):
    _name = 'campagne.levier'
    _description = 'Levier'

    name = fields.Char("Nom",required=True)

class Campagne(models.Model):
    _name = 'campagne.campagne'
    _description = 'Gestion des campagnes'
    _inherit = ['mail.thread']

    name = fields.Char("Nom", required=True)
    code = fields.Char("Code", required=True)
    date_start = fields.Date("Date début")
    date_end = fields.Date("Date fin")
    siege = fields.Boolean('Siège?')
    cible_id = fields.Many2one('campagne.cible',string='Cible')
    canal_id = fields.Many2one('campagne.canal',string='Canal')
    creation_comites = fields.Boolean("Création comités?")
    offre_ids = fields.One2many('campagne.offre', 'campagne_id', string="Offre")
    comite_ids = fields.Many2many('campagne.comite', string="Comités")
    comite_sysmarlig_ids = fields.Many2many('campagne.comite.sysmarlig', string="Comités sysmarlig")
    sf__id = fields.Char("Id sf",readonly=True)
    in_sysmarlig = fields.Boolean('Sysmarlig',readonly=True)
    audit_siege = fields.Boolean('Audit origine',readonly=True)
    audit_creation_comites = fields.Boolean('Audit création comités',readonly=True)
    audit_unique = fields.Boolean('Audit unicité',readonly=True)
    count_occurrence = fields.Integer("# occurrences", readonly=True)
    is_legacy = fields.Boolean('Historique')
    audit_canal = fields.Boolean('Audit canal',readonly=True)
    audit_cible = fields.Boolean('Audit cible',readonly=True)
    
    @api.constrains('date_start','date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and (record.date_start > record.date_end):
                raise ValidationError("La date de fin doit être supérieure à la date de début!")

    @api.constrains('siege')
    def _check_num_comites(self):
        for record in self:
            if (not record.siege) and (len(record.comite_ids) > 1 or len(record.comite_sysmarlig_ids) > 1):
                raise ValidationError("Un seul comité peut être associé à une campgne comité!")

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            duplicate = self.search([
                ('id', '!=', record.id),
                ('code', '=', record.code),
            ], limit=1)
            if duplicate:
                raise ValidationError("The code must be unique!")
    
    def action_synchroniser(self):
        for record in self:
            pass
            """
            sf = sf_api()
            query = f"SELECT Id,Name,LNCC_Code_Campagne__c,LNCC_Origine__c,LNCC_Comites_participants__c,LNCC_Comites_participants2__c FROM Campaign where LNCC_Code_Campagne__c='{record.code}' and RecordType.Name='Campagne'"
            print(query)
            res = sf.sf.query_all(query)
            print(res)
            print("action_synchroniser")
            """

class OffreCost(models.Model):
    _name = 'campagne.offre.cost'
    _description = 'Coût offre'

    offre_id = fields.Many2one('campagne.offre',string='Offre')
    qty = fields.Integer("Quantity", required=True)
    comite_id = fields.Many2one('campagne.comite', string="Comité",required=True)

class Offre(models.Model):
    _name = 'campagne.offre'
    _description = 'Gestion des offres'
    _inherit = ['mail.thread']

    name = fields.Char("Nom", required=True)
    code = fields.Char("Code", required=True)
    date_start = fields.Date("Date début")
    date_end = fields.Date("Date fin")
    siege = fields.Boolean('Siège?')
    campagne_id = fields.Many2one('campagne.campagne',string='Campagne')
    code_campagne = fields.Char(related='campagne_id.code',readonly=True)
    levier_id = fields.Many2one('campagne.levier',string='Levier')
    comite_ids = fields.Many2many('campagne.comite', string="Comités")
    comite_sysmarlig_ids = fields.Many2many('campagne.comite.sysmarlig', string="Comités sysmarlig")
    sf__id = fields.Char("Id sf",readonly=True)
    in_sysmarlig = fields.Boolean('Sysmarlig',readonly=True)
    audit_siege = fields.Boolean('Audit origine',readonly=True)
    audit_unique = fields.Boolean('Audit unicité',readonly=True)
    count_occurrence = fields.Integer("# occurrences", readonly=True)
    audit_levier = fields.Boolean('Audit levier',readonly=True)
    is_legacy = fields.Boolean('Historique')
    #DON
    don_account_id = fields.Many2one('account.account',string='Compte comptable (DON)')
    don_axe_1_id = fields.Many2one('account.analytic.account',string='Axe 1 (DON)',domain=[('type', '=', 'axe_1')])
    don_axe_2_id = fields.Many2one('account.analytic.account',string='Axe 2 (DON)',domain=[('type', '=', 'axe_2_3')])
    don_axe_3_id = fields.Many2one('account.analytic.account',string='Axe 3 (DON)',domain=[('type', '=', 'axe_2_3')])
    #COTIS
    cotis_account_id = fields.Many2one('account.account',string='Compte comptable (Cotisation)')
    cotis_axe_1_id = fields.Many2one('account.analytic.account',string='Axe 1 (Cotisation)',domain=[('type', '=', 'axe_1')])
    cotis_axe_2_id = fields.Many2one('account.analytic.account',string='Axe 2 (Cotisation)',domain=[('type', '=', 'axe_2_3')])
    cotis_axe_3_id = fields.Many2one('account.analytic.account',string='Axe 3 (Cotisation)',domain=[('type', '=', 'axe_2_3')])
    cotis_amount = fields.Float("Montant cotisation")
    #VIVRE
    vivre_account_id = fields.Many2one('account.account',string='Compte comptable (Vivre)')
    vivre_axe_1_id = fields.Many2one('account.analytic.account',string='Axe 1 (Vivre)',domain=[('type', '=', 'axe_1')])
    vivre_axe_2_id = fields.Many2one('account.analytic.account',string='Axe 2 (Vivre)',domain=[('type', '=', 'axe_2_3')])
    vivre_axe_3_id = fields.Many2one('account.analytic.account',string='Axe 3 (Vivre)',domain=[('type', '=', 'axe_2_3')])
    vivre_amount = fields.Float("Montant vivre")
    #VENTE
    vente_account_id = fields.Many2one('account.account',string='Compte comptable (Vente)')
    vente_axe_1_id = fields.Many2one('account.analytic.account',string='Axe 1 (Vente)',domain=[('type', '=', 'axe_1')])
    vente_axe_2_id = fields.Many2one('account.analytic.account',string='Axe 2 (Vente)',domain=[('type', '=', 'axe_2_3')])
    vente_axe_3_id = fields.Many2one('account.analytic.account',string='Axe 3 (Vente)',domain=[('type', '=', 'axe_2_3')])
    vente_amount = fields.Float("Montant vente")
    #PROD
    prod_account_id = fields.Many2one('account.account',string='Compte comptable (Prod annexes)')
    prod_axe_1_id = fields.Many2one('account.analytic.account',string='Axe 1 (Prod annexes)',domain=[('type', '=', 'axe_1')])
    prod_axe_2_id = fields.Many2one('account.analytic.account',string='Axe 2 (Prod annexes)',domain=[('type', '=', 'axe_2_3')])
    prod_axe_3_id = fields.Many2one('account.analytic.account',string='Axe 3 (Prod annexes)',domain=[('type', '=', 'axe_2_3')])
    prod_amount = fields.Float("Montant prod annexes")

    unit_cost = fields.Float("Coût unitaire")
    qty_lines_ids = fields.One2many('campagne.offre.cost','offre_id',string='Quantités comités')

    def action_synchroniser(self):
        for record in self:
            pass
    
    @api.constrains('date_start','date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and (record.date_start > record.date_end):
                raise ValidationError("La date de fin doit être supérieure à la date de début!")
    
    @api.constrains('siege')
    def _check_num_comites(self):
        for record in self:
            if (not record.siege) and (len(record.comite_ids) > 1 or len(record.comite_sysmarlig_ids) > 1):
                raise ValidationError("Un seul comité peut être associé à une offere comité!")

    @api.constrains('code', 'campagne_id')
    def _check_code_campagne_unique(self):
        for record in self:
            duplicate = self.search([
                ('id', '!=', record.id),
                ('code', '=', record.code), 
                ('campagne_id', '=', record.campagne_id.id),
            ], limit=1)
            if duplicate:
                print(record.code, record.campagne_id.code)
                raise ValidationError("The combination of name and campagne must be unique!")
    
    def add_offre_qty(self,data,sf):
        endpoint = 'solliciteoffre'
        response = sf.sf.apexecute(endpoint, method='POST', data=data)
        return response

    def export_qty(self):
        mode = os.getenv('mode')
        sf = sf_api(mode=mode)
        for rec in self:
            if rec.sf__id:
                res_update = sf.sf.Campaign.update(rec.sf__id,{'LNCC_Cout_unitaire__c': rec.unit_cost})
                rec.message_post(body=f"Qty update status: {res_update}", body_is_html =True)
                data = [{"code_comite" : l.comite_id.name,"id_offre":rec.sf__id,"quantite":l.qty} for l in rec.qty_lines_ids]
                print(data)
                res = self.add_offre_qty(data,sf)
                rec.message_post(body=res, body_is_html =True)
    
