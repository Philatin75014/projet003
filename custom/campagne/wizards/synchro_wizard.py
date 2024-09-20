from odoo import models, fields, api
from odoo.exceptions import ValidationError
import os
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

class sf_api:
    def get_access_token(self,login_url,client_id,client_secret):
        login_url = f'{login_url}/services/oauth2/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
        response = requests.post(login_url, data=data)
        return response.json().get("access_token"), response.json().get("instance_url")

    def __init__(self,mode):
        if mode == 'test':
            test_login_url = os.getenv('test_login_url')
            test_client_id = os.getenv('test_client_id')
            test_client_secret = os.getenv('test_client_secret')
            access_token,instance_url = self.get_access_token(test_login_url,test_client_id,test_client_secret)
            self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
        elif mode == 'prod':
            prod_login_url = os.getenv('prod_login_url')
            prod_client_id = os.getenv('prod_client_id')
            prod_client_secret = os.getenv('prod_client_secret')
            access_token,instance_url = self.get_access_token(prod_login_url,prod_client_id,prod_client_secret)
            self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
        else:
            raise Exception("Only test and prod are accepted!")

class exportWizard(models.TransientModel):
    _name = 'export.wizard'
    _description = 'Export Donalig'

    def _get_mode(self):
        return os.getenv('mode')

    mode = fields.Selection([
        ('test', 'PreProd'),
        ('prod', 'Prod')
    ], string='Mode',required=True,readonly=True,default=_get_mode)

    box_update = fields.Boolean("Cocher / Décocher")

    operation = fields.Selection([
        ('insert', 'Création'),
        ('update', 'MAJ')
    ], string='Opération',required=True)  

    #all
    name = fields.Boolean("Nom")
    code = fields.Boolean("Code")
    date_start = fields.Boolean("Date de début")
    date_end = fields.Boolean("Date de fin")
    siege = fields.Boolean("Origine")
    comites = fields.Boolean("Comites")
    #campagne
    cible = fields.Boolean("Cible")
    canal = fields.Boolean("Canal")
    creation_comites = fields.Boolean("Création comités")
    #Offre
    levier = fields.Boolean("Levier")
    accounts = fields.Boolean("Comptes et axes comptables")
    campagne = fields.Boolean("Campagne")

    active_model_name = fields.Char(string="Active Model", readonly=True)


    def get_status_and_error_for_id(self,update_results, id):
        for result in update_results:
            if result['id'] == id:
                return {
                    'success': result['success'],
                    'errors': result.get('errors', [])
                }
        return {'success': None, 'errors': []}



    def log_export_ops(self, export_ops_list, sf_list=None):
        filtered_data = [item for item in export_ops_list if item['model_id'] in sf_list]
        self.env['export.ops'].create(filtered_data)

    @api.onchange('box_update')
    def boxes_updates(self):
        if self.box_update:
            self.edit_boxes(True)
        else:
            self.edit_boxes(False)

    def edit_boxes(self,state):
        for rec in self:
            rec.name = state
            rec.code = state
            rec.date_start = state
            rec.date_end = state
            rec.siege = state
            rec.comites = state
            if self.active_model_name == 'campagne.campagne':
                rec.cible = state
                rec.canal = state
                rec.creation_comites = state
                rec.accounts = state
            if self.active_model_name == 'campagne.offre':
                rec.levier = state
                rec.accounts = state
                rec.campagne = state

    @api.model
    def default_get(self, fields):
        res = super(exportWizard, self).default_get(fields)
        res['active_model_name'] = self._context.get('active_model', False)
        return res

    def get_record_type(self,SobjectType,Name=None):
        sf = sf_api(self.mode)
        soql_query = f"select Id, Name, SobjectType from RecordType where SobjectType = '{SobjectType}'"
        query_results = sf.sf.query_all(soql_query,timeout=30)
        data = pd.DataFrame(query_results['records']).drop(columns='attributes')
        if Name:
            record_id = data.loc[(data['Name'] == Name)].iloc[0].to_dict()['Id']
            return record_id
        else:
            return data
    
    def get_accounts(self,data,rec):
        if rec.don_account_id:
            data['LNCC_Compte_Comptable_Don_LU__c'] = rec.don_account_id.sf__id
            if rec.don_axe_1_id:
                data['LNCC_Axe_1__c'] = rec.don_axe_1_id.sf__id
            if rec.don_axe_2_id:
                data['LNCC_Axe_2__c'] = rec.don_axe_2_id.sf__id
            if rec.don_axe_3_id:
                data['LNCC_DON_Axe_3__c'] = rec.don_axe_3_id.sf__id
        if rec.cotis_account_id:
            data['LNCC_Compte_Comptable_Cotisation_LU__c'] = rec.cotis_account_id.sf__id
            data['LNCC_Seuil_Cotisation__c'] = rec.cotis_amount
            if rec.cotis_axe_1_id:
                data['LNCC_COTIS_Axe_1__c'] = rec.cotis_axe_1_id.sf__id
            if rec.cotis_axe_2_id:
                data['LNCC_COTIS_Axe_2__c'] = rec.cotis_axe_2_id.sf__id
            if rec.cotis_axe_3_id:
                data['LNCC_COTIS_Axe_3__c'] = rec.cotis_axe_3_id.sf__id
        if rec.vivre_account_id:
            data['LNCC_VIVRE_Compte_Comptable__c'] = rec.vivre_account_id.sf__id
            data['LNCC_Abonnement_VIVRE__c'] = rec.vivre_amount
            if rec.vivre_axe_1_id:
                data['LNCC_VIVRE_Axe_1__c'] = rec.vivre_axe_1_id.sf__id
            if rec.vivre_axe_2_id:
                data['LNCC_VIVRE_Axe_2__c'] = rec.vivre_axe_2_id.sf__id
            if rec.vivre_axe_3_id:
                data['LNCC_VIVRE_Axe_3__c'] = rec.vivre_axe_3_id.sf__id
        if rec.vente_account_id:
            data['LNCC_VENTE_Compte_Comptable__c'] = rec.vente_account_id.sf__id
            data['LNCC_Montant_Vente__c'] = rec.vente_amount
            if rec.vente_axe_1_id:
                data['LNCC_VENTE_Axe_1__c'] = rec.vente_axe_1_id.sf__id
            if rec.vente_axe_2_id:
                data['LNCC_VENTE_Axe_2__c'] = rec.vente_axe_2_id.sf__id
            if rec.vente_axe_3_id:
                data['LNCC_VENTE_Axe_3__c'] = rec.vente_axe_3_id.sf__id
        if rec.prod_account_id:
            data['LNCC_PROD_ANNEXES_Compte_Comptable__c'] = rec.prod_account_id.sf__id
            data['LNCC_Montant_ProdAnnexes__c'] = rec.prod_amount
            if rec.prod_axe_1_id:
                data['LNCC_PROD_ANNEXES_Axe_1__c'] = rec.prod_axe_1_id.sf__id
            if rec.prod_axe_2_id:
                data['LNCC_PROD_ANNEXES_Axe_2__c'] = rec.prod_axe_2_id.sf__id
            if rec.prod_axe_3_id:
                data['LNCC_PROD_ANNEXES_Axe_3__c'] = rec.prod_axe_3_id.sf__id
    
    def action_export(self):
        self.action_export_model()
        active_model = self._context.get('active_model')
        if active_model == 'campagne.campagne':
            active_ids = self._context.get('active_ids')
            records = self.env[active_model].browse(active_ids)
            for cam in records:
                if cam.offre_ids:
                    self.action_export_model(active_ids=cam.offre_ids.ids,active_model='campagne.offre')

    def action_export_model(self,active_ids=None,active_model=None):
        if not active_ids:
            active_ids = self._context.get('active_ids')
        if not active_model:
            active_model = self._context.get('active_model')
        records = self.env[active_model].browse(active_ids)
        sf = sf_api(self.mode)
        if self.operation == 'update':
            is_sf_id = [rec.sf__id == False for rec in records]
            if any(is_sf_id):
                raise ValidationError("Certaines données ne sont pas créées dans Donalig!")
            update_list = []
            export_ops_list = []
            code_field = False
            if active_model == 'campagne.campagne':
                record_type_id = self.get_record_type('Campaign','Campagne')
                code_field = 'LNCC_Code_Campagne__c'
            if active_model == 'campagne.offre':
                record_type_id = self.get_record_type('Campaign','Offres')
                code_field = 'LNCC_Code_offre__c'
            for rec in records:
                data = {}
                export_data = {
                    'model_id': rec.id,
                    'model_name': active_model,
                    'mode': self.mode,
                    'operation': self.operation,
                }
                if self.campagne:
                    if not rec.campagne_id.sf__id:
                        raise ValidationError(f"La campagne {rec.campagne_id.code} n'a pas d'id Donalig!")
                    data['ParentId'] = rec.campagne_id.sf__id
                    export_data['campagne'] = True
                if self.name:
                    data['Name'] = rec.name
                    export_data['name'] = True
                if self.code:
                    data[code_field] = rec.code
                    export_data['code'] = True
                if self.date_start and rec.date_start:
                    data['StartDate'] = rec.date_start.strftime('%Y-%m-%d')
                    export_data['date_start'] = True
                if self.date_end and rec.date_end:
                    data['EndDate'] = rec.date_end.strftime('%Y-%m-%d')
                    export_data['date_end'] = True
                if self.siege:
                    data['LNCC_Origine__c'] = 'SIEGE' if rec.siege else 'COMITE'
                    export_data['siege'] = True
                if self.cible and active_model == 'campagne.campagne':
                    data['LNCC_Cible__c'] = rec.cible_id.name
                    export_data['cible'] = True
                if self.canal and active_model == 'campagne.campagne':
                    data['LNCC_Canal__c'] = rec.canal_id.name
                    export_data['canal'] = True
                if self.levier and active_model == 'campagne.offre':
                    data['LNCC_Levier__c'] = rec.levier_id.name
                    export_data['levier'] = True
                if self.creation_comites and active_model == 'campagne.campagne':
                    data['LNCC_Autoriser_comites_creer_offres__c'] = rec.creation_comites
                    export_data['creation_comites'] = True
                if self.comites:
                    data['LNCC_Comites_participants__c'] = ";".join(comite.name for comite in rec.comite_ids if int(comite.name[-3:]) <= 50)
                    data['LNCC_Comites_participants2__c'] = ";".join(comite.name for comite in rec.comite_ids if int(comite.name[-3:]) > 50)
                    export_data['comites'] = True
                if self.accounts and  active_model == 'campagne.offre':
                    export_data['accounts'] = True
                    self.get_accounts(data,rec)
                if data:
                    data['Id'] = rec.sf__id
                    update_list.append(data)
                    export_ops_list.append(export_data)
            if update_list:
                results = sf.sf.bulk.Campaign.update(update_list,batch_size=10000)
                sf_update = []
                for rec in records:
                    rep = self.get_status_and_error_for_id(results, rec.sf__id)
                    if rep.get('success',False) == False and rep.get('errors',False):
                        html_message = "<table style='width:100%; border-collapse: collapse;'>"
                        html_message += "<tr><th style='border: 1px solid black;'>Error Code</th><th style='border: 1px solid black;'>Message</th><th style='border: 1px solid black;'>Fields</th></tr>"
                        for item in rep['errors']:
                            html_message += f"<tr><td style='border: 1px solid black;'>{item['statusCode']}</td><td style='border: 1px solid black;'>{item['message']}</td><td style='border: 1px solid black;'>{item['fields']}</td></tr>"

                        html_message += "</table>"
                        rec.message_post(body=html_message, body_is_html =True)
                    else:
                        sf_update.append(rec.id)
                        rec.message_post(body=f'Update request sent!')
                self.log_export_ops(export_ops_list,sf_update)

        if self.operation == 'insert':
            is_legacy = [rec.is_legacy for rec in records]
            if any(is_legacy):
                raise ValidationError("Données historiques sélectionnées!")
            is_sf_id = [rec.sf__id for rec in records]
            if any(is_sf_id):
                raise ValidationError("Certaines données sont déjà créées dans Donalig!")
            insert_list = []
            export_ops_list = []
            record_type_id = False
            code_field = False
            if active_model == 'campagne.campagne':
                record_type_id = self.get_record_type('Campaign','Campagne')
                code_field = 'LNCC_Code_Campagne__c'
            if active_model == 'campagne.offre':
                record_type_id = self.get_record_type('Campaign','Offres')
                code_field = 'LNCC_Code_offre__c'
            for rec in records:
                data = {}
                export_data = {
                    'model_id': rec.id,
                    'model_name': active_model,
                    'mode': self.mode,
                    'operation': self.operation,
                }
                data['rec'] = rec
                if active_model == 'campagne.offre':
                    data['ParentId'] = rec.campagne_id.sf__id
                if self.name:
                    data['Name'] = rec.name
                    export_data['name'] = True
                if self.code:
                    data[code_field] = rec.code
                    export_data['code'] = True
                if self.date_start and rec.date_start:
                    data['StartDate'] = rec.date_start.strftime('%Y-%m-%d')
                    export_data['date_start'] = True
                if self.date_end and rec.date_end:
                    data['EndDate'] = rec.date_end.strftime('%Y-%m-%d')
                    export_data['date_end'] = True
                if self.siege:
                    data['LNCC_Origine__c'] = 'SIEGE' if rec.siege else 'COMITE'
                    export_data['siege'] = True
                if self.cible and active_model == 'campagne.campagne':
                    data['LNCC_Cible__c'] = rec.cible_id.name
                    export_data['cible'] = True
                if self.canal and active_model == 'campagne.campagne':
                    data['LNCC_Canal__c'] = rec.canal_id.name
                    export_data['canal'] = True
                if self.levier and active_model == 'campagne.offre':
                    data['LNCC_Levier__c'] = rec.levier_id.name
                    export_data['levier'] = True
                if self.creation_comites and active_model == 'campagne.campagne':
                    data['LNCC_Autoriser_comites_creer_offres__c'] = rec.creation_comites
                    export_data['creation_comites'] = True
                if self.accounts and  active_model == 'campagne.offre':
                    self.get_accounts(data,rec)
                    export_data['accounts'] = True
                if data:
                    data['RecordTypeId'] = record_type_id
                    if self.comites and rec.siege:
                        data['LNCC_Comites_participants__c'] = ";".join(comite.name for comite in rec.comite_ids if int(comite.name[-3:]) <= 50)
                        data['LNCC_Comites_participants2__c'] = ";".join(comite.name for comite in rec.comite_ids if int(comite.name[-3:]) > 50)
                        export_data['comites'] = True
                        insert_list.append(data)
                        export_ops_list.append(export_data)
                    if self.comites and not rec.siege:
                        for comite in rec.comite_ids:
                            d_comite = data.copy() 
                            if int(comite.name[-3:]) <= 50:
                                d_comite['LNCC_Comites_participants__c'] = comite.name 
                            else:
                                d_comite['LNCC_Comites_participants2__c'] = comite.name
                            export_data['comites'] = True
                            insert_list.append(d_comite)
                            export_ops_list.append(export_data)
            if insert_list:
                sf_insert = []
                for rec in insert_list:
                    sf_rec = {k: v for k, v in rec.items() if k != 'rec'}
                    try:
                        sf_res = sf.sf.Campaign.create(sf_rec)
                        print("sf_res",sf_res)
                        if sf_res.get('id'):
                            rec['rec'].write({'sf__id': sf_res.get('id')})
                            rec['rec'].message_post(body=f"Record created: {sf_res.get('id')}")
                            sf_insert.append(rec['rec'].id)
                    except SalesforceMalformedRequest as e:
                        if e:
                            html_message = "<table style='width:100%; border-collapse: collapse;'>"
                            html_message += "<tr><th style='border: 1px solid black;'>Error Code</th><th style='border: 1px solid black;'>Message</th></tr>"

                            for item in e.content:
                                html_message += f"<tr><td style='border: 1px solid black;'>{item['errorCode']}</td><td style='border: 1px solid black;'>{item['message']}</td></tr>"

                            html_message += "</table>"
                            rec['rec'].message_post(body=html_message, body_is_html =True)
                self.log_export_ops(export_ops_list,sf_insert)

class synchroWizard(models.TransientModel):
    _name = 'synchro.wizard'
    _description = 'Synchronisation Donalig'

    type = fields.Selection([
        ('account', 'Compte comptable'),
        ('axe', 'Axe analytique'),
        ('offre', 'Offre'),
        ('campagne', 'Campagne')
    ], string='Object',required=True)

    def _get_mode(self):
        return os.getenv('mode')

    mode = fields.Selection([
        ('test', 'PreProd'),
        ('prod', 'Prod')
    ], string='Mode',required=True,readonly=True,default=_get_mode)    

    update = fields.Boolean("MAJ")

    def get_res(self,query):
        sf = sf_api(self.mode)
        res = sf.sf.query_all(query)
        if res['totalSize'] > 0:
            df = pd.DataFrame(res['records']).drop(columns='attributes')
            return df
        else:
            return pd.DataFrame()
    
    def create_comite(self,list_comite):
        for comite in list_comite:
            comite_id = self.env['campagne.comite'].search([('name','=',comite)])
            if not comite_id:
                self.env['campagne.comite'].create({'name':comite})

    def update_campagne(self,df,update):
        campagne_obj = self.env['campagne.campagne']
        exploded_df = df.explode('comite_ids')
        list_comite = exploded_df['comite_ids'].unique().tolist()
        self.create_comite(list_comite)
        comites = self.env['campagne.comite'].search([])
        comite_dict = {comite.name: comite.id for comite in comites}  
        for campagne in campagne_obj.search([]):
            filtered_df = df.loc[df['code'] == campagne.code]
            if not filtered_df.empty:
                row_dict = filtered_df.iloc[0].to_dict()
            else:
                row_dict = None
            if row_dict:
                comite_list_ids = [comite_dict[code] for code in row_dict['comite_ids'] if code in comite_dict]
                comite_ids = [(6, 0, comite_list_ids)]
                audit_creation_comites = False
                audit_unique = False
                audit_siege = False
                audit_canal = False
                audit_cible = False
                if campagne.creation_comites != row_dict['creation_comites']:
                    audit_creation_comites = True
                if row_dict['count_occurrence'] > 1:
                    audit_unique = True
                if campagne.siege != row_dict['siege']:
                    audit_siege = True
                if campagne.canal_id.name != row_dict['canal_id']:
                    audit_canal = True
                if campagne.cible_id.name != row_dict['cible_id']:
                    audit_cible = True
                vals = {
                    'audit_creation_comites': audit_creation_comites,
                    'audit_unique': audit_unique,
                    'audit_siege': audit_siege,
                    'audit_canal': audit_canal,
                    'audit_cible': audit_cible,
                    'sf__id': row_dict['sf__id'],
                    'date_start': row_dict['date_start'],
                    'date_end': row_dict['date_end'],
                    'count_occurrence': row_dict['count_occurrence'],
                    'comite_ids': comite_ids,
                }
                if not update:
                    vals = {
                    'audit_creation_comites': audit_creation_comites,
                    'audit_unique': audit_unique,
                    'audit_siege': audit_siege,
                    'audit_canal': audit_canal,
                    'audit_cible': audit_cible,
                    'sf__id': row_dict['sf__id'],
                    'count_occurrence': row_dict['count_occurrence'],
                    }   
                campagne.write(vals)
    
    def amount_float(self,amount):
        try:
            return float(amount)
        except ValueError:
            return 0.0
    
    def update_offre(self,df,update):
        offre_obj = self.env['campagne.offre']
        amount_cols = ['cotis_amount', 'vivre_amount','vente_amount','prod_amount']
        df.loc[:,amount_cols] = df.loc[:,amount_cols].fillna(0)
        exploded_df = df.explode('comite_ids')
        list_comite = exploded_df['comite_ids'].unique().tolist()
        self.create_comite(list_comite)
        comites = self.env['campagne.comite'].search([])
        comite_dict = {comite.name: comite.id for comite in comites}
        accounts = self.env['account.account'].search([])
        account_dict = {account.code: account.id for account in accounts}
        axes = self.env['account.analytic.account'].search([])
        axe_dict = {axe.code: axe.id for axe in axes}  
        for offre in offre_obj.search([]):
            filtered_df = df.loc[(df['code'] == offre.code) & (df['campagne_id'] == offre.code_campagne) & (df['siege'] == offre.siege)]
            if not filtered_df.empty:
                row_dict = filtered_df.iloc[0].to_dict()
            else:
                row_dict = None
            if row_dict:
                comite_list_ids = [comite_dict[code] for code in row_dict['comite_ids'] if code in comite_dict]
                comite_ids = [(6, 0, comite_list_ids)]
                audit_unique = False
                audit_siege = False
                audit_levier = False
                if row_dict['count_occurrence'] > 1:
                    audit_unique = True
                if offre.siege != row_dict['siege']:
                    audit_siege = True
                if offre.levier_id != row_dict['levier_id']:
                    audit_levier = True
                vals = {
                    'audit_unique': audit_unique,
                    'audit_siege': audit_siege,
                    'audit_levier': audit_levier,
                    'sf__id': row_dict['sf__id'],
                    'date_start': row_dict['date_start'],
                    'date_end': row_dict['date_end'],
                    'count_occurrence': row_dict['count_occurrence'],
                    'comite_ids': comite_ids,
                    'don_account_id': account_dict.get(row_dict['don_account_id'],False),
                    'don_axe_1_id': axe_dict.get(row_dict['don_axe_1_id'],False),
                    'don_axe_2_id': axe_dict.get(row_dict['don_axe_2_id'],False),
                    'don_axe_3_id': axe_dict.get(row_dict['don_axe_3_id'],False),
                    'cotis_account_id': account_dict.get(row_dict['cotis_account_id'],False),
                    'cotis_axe_1_id': axe_dict.get(row_dict['cotis_axe_1_id'],False),
                    'cotis_axe_2_id': axe_dict.get(row_dict['cotis_axe_2_id'],False),
                    'cotis_axe_3_id': axe_dict.get(row_dict['cotis_axe_3_id'],False),
                    'cotis_amount': self.amount_float(row_dict['cotis_amount']),
                    'vivre_account_id': account_dict.get(row_dict['vivre_account_id'],False),
                    'vivre_axe_1_id': axe_dict.get(row_dict['vivre_axe_1_id'],False),
                    'vivre_axe_2_id': axe_dict.get(row_dict['vivre_axe_2_id'],False),
                    'vivre_axe_3_id': axe_dict.get(row_dict['vivre_axe_3_id'],False),
                    'vivre_amount': self.amount_float(row_dict['vivre_amount']),
                    'vente_account_id': account_dict.get(row_dict['vente_account_id'],False),
                    'vente_axe_1_id': axe_dict.get(row_dict['vente_axe_1_id'],False),
                    'vente_axe_2_id': axe_dict.get(row_dict['vente_axe_2_id'],False),
                    'vente_axe_3_id': axe_dict.get(row_dict['vente_axe_3_id'],False),
                    'vente_amount': self.amount_float(row_dict['vente_amount']),
                    'prod_account_id': account_dict.get(row_dict['prod_account_id'],False),
                    'prod_axe_1_id': axe_dict.get(row_dict['prod_axe_1_id'],False),
                    'prod_axe_2_id': axe_dict.get(row_dict['prod_axe_2_id'],False),
                    'prod_axe_3_id': axe_dict.get(row_dict['prod_axe_3_id'],False),
                    'prod_amount': self.amount_float(row_dict['prod_amount']),
                }
                if not update:
                    vals = {
                    'audit_unique': audit_unique,
                    'audit_siege': audit_siege,
                    'audit_levier': audit_levier,
                    'sf__id': row_dict['sf__id'],
                    'count_occurrence': row_dict['count_occurrence'],
                    }   
                offre.write(vals)

    def extract_name(self,field):
        if pd.notna(field):
            name = field.get('Name', None)
            return name
        return None
    
    def extract_campagne(self,field):
        if pd.notna(field):
            name = field.get('LNCC_Code_Campagne__c', None)
            return name
        return None
    
    def extract_campagne_origine(self,field):
        if pd.notna(field):
            name = field.get('LNCC_Origine__c', None)
            return name
        return None
    
    def action_sync(self):
        if self.type == 'account':
            query = f"select id,Name, Libelle__c, RecordType.Name from LNCC_Compte_Comptable__c"
            df = self.get_res(query)
            if df.size > 0:
                account_obj = self.env['account.account']
                df['RecordTypeName'] = df['RecordType'].apply(lambda x: x.get('Name') if pd.notnull(x) else None)
                df['account_type'] = df['RecordTypeName'].apply(lambda x: 'asset_cash' if x == 'Compte de Banque' else 'income' if x == 'Compte général' else None)
                df = df.drop(columns=['RecordType','RecordTypeName'])
                df.rename(columns={'Name': 'code', 'Libelle__c': 'name', 'Id': 'sf__id'}, inplace=True)
                df['count_occurrence'] = df.groupby('code')['code'].transform('count')
                df = df.drop_duplicates(subset='code')
                code_list = [r['code'] for r in account_obj.search([]).read(['code'])]
                df_insert = df[~df['code'].isin(code_list)]
                account_recs = df_insert.to_dict('records')
                account_obj.create(account_recs)
        if self.type == 'axe':
            query = f"select id,Name, Libelle__c, RecordType.Name from Compte_Analytique__c"
            df = self.get_res(query)
            if df.size > 0:
                axe_obj = self.env['account.analytic.account']
                df['RecordTypeName'] = df['RecordType'].apply(lambda x: x.get('Name') if pd.notnull(x) else None)
                df['type'] = df['RecordTypeName'].apply(lambda x: 'axe_1' if x == 'Axe 1' else 'axe_2_3' if x == 'Axe 2 ou 3' else None)
                df = df.drop(columns=['RecordType','RecordTypeName'])
                df.rename(columns={'Name': 'code', 'Libelle__c': 'name', 'Id': 'sf__id'}, inplace=True)
                df['count_occurrence'] = df.groupby('code')['code'].transform('count')
                df = df.drop_duplicates(subset='code')
                code_list = [r['code'] for r in axe_obj.search([]).read(['code'])]
                df_insert = df[~df['code'].isin(code_list)]
                axe_recs = df_insert.to_dict('records')
                axe_obj.create(axe_recs)
        if self.type == 'campagne':
            query = f"""select id,Name,LNCC_Code_Campagne__c,LNCC_Origine__c,LNCC_Cible__c,LNCC_Canal__c,StartDate,EndDate,LNCC_Autoriser_comites_creer_offres__c,LNCC_Comites_participants__c,LNCC_Comites_participants2__c 
                        from Campaign 
                        where RecordType.Name = 'Campagne' and  LNCC_Origine__c = 'SIEGE'"""
            df = self.get_res(query)
            if df.size > 0:
                def merge_comite(row):
                    vals = []
                    if pd.notnull(row['LNCC_Comites_participants__c']):
                        vals.extend(row['LNCC_Comites_participants__c'].split(';'))
                    if pd.notnull(row['LNCC_Comites_participants2__c']):
                        vals.extend(row['LNCC_Comites_participants2__c'].split(';'))
                    return vals
                campagne_obj = self.env['campagne.campagne']
                df['siege'] = df['LNCC_Origine__c'].apply(lambda x: True if x == 'SIEGE' else False)
                df['comite_ids'] = df.apply(merge_comite, axis=1)
                df = df.drop(columns=['LNCC_Origine__c','LNCC_Comites_participants__c','LNCC_Comites_participants2__c'])
                df.rename(columns={'Name': 'name', 'LNCC_Code_Campagne__c': 'code', 'Id': 'sf__id','StartDate':'date_start','EndDate':'date_end',
                                   'LNCC_Autoriser_comites_creer_offres__c':'creation_comites','LNCC_Canal__c':'canal_id','LNCC_Cible__c':'cible_id'}, inplace=True)
                df['count_occurrence'] = df.groupby('code')['code'].transform('count')
                df = df.drop_duplicates(subset='code')
                code_list = [r['code'] for r in campagne_obj.search([]).read(['code'])]
                df_missing = df[~df['code'].isin(code_list) & (df['siege'] == True)]
                df_update = df[df['code'].isin(code_list)]
                missig_log_df = df_missing[['sf__id','code']].rename(columns={'code': 'name'})
                log_id = self.env['campagne.log'].create({'name':'Campagnes'})
                missig_log_df['log_id'] = log_id.id
                log_recs = missig_log_df.to_dict('records')
                self.env['campagne.log.line'].create(log_recs)
                self.update_campagne(df_update,self.update)
        if self.type == 'offre':
            query = f"""select id,Name,Parent.LNCC_Code_Campagne__c,Parent.LNCC_Origine__c,LNCC_Levier__c,LNCC_Code_offre__c,LNCC_Origine__c,StartDate,EndDate,LNCC_Comites_participants__c,LNCC_Comites_participants2__c,LNCC_Compte_Comptable_Don_LU__r.Name,
                        LNCC_Axe_1__r.Name,LNCC_Axe_2__r.Name,LNCC_DON_Axe_3__r.Name,LNCC_Compte_Comptable_Cotisation_LU__r.name, LNCC_COTIS_Axe_1__r.Name, LNCC_COTIS_Axe_2__r.Name, LNCC_COTIS_Axe_3__r.Name, LNCC_Seuil_Cotisation__c, LNCC_VIVRE_Compte_Comptable__r.Name, LNCC_VIVRE_Axe_1__r.Name, LNCC_VIVRE_Axe_2__r.Name, LNCC_VIVRE_Axe_3__r.Name, LNCC_Abonnement_VIVRE__c, LNCC_VENTE_Compte_Comptable__r.Name, LNCC_VENTE_Axe_1__r.Name, LNCC_VENTE_Axe_2__r.Name, LNCC_VENTE_Axe_3__r.Name, LNCC_Montant_Vente__c, LNCC_PROD_ANNEXES_Compte_Comptable__r.name, LNCC_PROD_ANNEXES_Axe_1__r.Name, LNCC_PROD_ANNEXES_Axe_2__r.Name, LNCC_PROD_ANNEXES_Axe_3__r.Name, LNCC_Montant_ProdAnnexes__c
                        from Campaign 
                        where RecordType.Name = 'Offres' and Parent.LNCC_Origine__c = 'SIEGE'
                        """
            df = self.get_res(query)
            if df.size > 0:
                def merge_comite(row):
                    vals = []
                    if pd.notnull(row['LNCC_Comites_participants__c']):
                        vals.extend(row['LNCC_Comites_participants__c'].split(';'))
                    if pd.notnull(row['LNCC_Comites_participants2__c']):
                        vals.extend(row['LNCC_Comites_participants2__c'].split(';'))
                    return vals
                offre_obj = self.env['campagne.offre']
                df['siege'] = df['LNCC_Origine__c'].apply(lambda x: True if x == 'SIEGE' else False)
                df['comite_ids'] = df.apply(merge_comite, axis=1)
                df.rename(columns={'Name': 'name', 'LNCC_Code_Campagne__c': 'code', 'Id': 'sf__id','StartDate':'date_start','EndDate':'date_end',
                                   'LNCC_Autoriser_comites_creer_offres__c':'creation_comites','LNCC_Seuil_Cotisation__c':'cotis_amount','LNCC_Abonnement_VIVRE__c':'vivre_amount',
                                   'LNCC_Montant_Vente__c':'vente_amount','LNCC_Montant_ProdAnnexes__c':'prod_amount','LNCC_Code_offre__c':'code','LNCC_Levier__c':'levier_id'}, inplace=True)
                df['campagne_id'] = df['Parent'].apply(self.extract_campagne)
                df['campagne_origine'] = df['Parent'].apply(self.extract_campagne_origine)
                df['don_account_id'] = df['LNCC_Compte_Comptable_Don_LU__r'].apply(self.extract_name)
                df['don_axe_1_id'] = df['LNCC_Axe_1__r'].apply(self.extract_name)
                df['don_axe_2_id'] = df['LNCC_Axe_2__r'].apply(self.extract_name)
                df['don_axe_3_id'] = df['LNCC_DON_Axe_3__r'].apply(self.extract_name)
                df['cotis_account_id'] = df['LNCC_Compte_Comptable_Cotisation_LU__r'].apply(self.extract_name)
                df['cotis_axe_1_id'] = df['LNCC_COTIS_Axe_1__r'].apply(self.extract_name)
                df['cotis_axe_2_id'] = df['LNCC_COTIS_Axe_2__r'].apply(self.extract_name)
                df['cotis_axe_3_id'] = df['LNCC_COTIS_Axe_3__r'].apply(self.extract_name)
                df['vivre_account_id'] = df['LNCC_VIVRE_Compte_Comptable__r'].apply(self.extract_name)
                df['vivre_axe_1_id'] = df['LNCC_VIVRE_Axe_1__r'].apply(self.extract_name)
                df['vivre_axe_2_id'] = df['LNCC_VIVRE_Axe_2__r'].apply(self.extract_name)
                df['vivre_axe_3_id'] = df['LNCC_VIVRE_Axe_3__r'].apply(self.extract_name)
                df['vente_account_id'] = df['LNCC_VENTE_Compte_Comptable__r'].apply(self.extract_name)
                df['vente_axe_1_id'] = df['LNCC_VENTE_Axe_1__r'].apply(self.extract_name)
                df['vente_axe_2_id'] = df['LNCC_VENTE_Axe_2__r'].apply(self.extract_name)
                df['vente_axe_3_id'] = df['LNCC_VENTE_Axe_3__r'].apply(self.extract_name)
                df['prod_account_id'] = df['LNCC_PROD_ANNEXES_Compte_Comptable__r'].apply(self.extract_name)
                df['prod_axe_1_id'] = df['LNCC_PROD_ANNEXES_Axe_1__r'].apply(self.extract_name)
                df['prod_axe_2_id'] = df['LNCC_PROD_ANNEXES_Axe_2__r'].apply(self.extract_name)
                df['prod_axe_3_id'] = df['LNCC_PROD_ANNEXES_Axe_3__r'].apply(self.extract_name)
                df = df.drop(columns=['LNCC_Origine__c','LNCC_Comites_participants__c','LNCC_Comites_participants2__c','Parent','LNCC_Compte_Comptable_Don_LU__r',
                                      'LNCC_Axe_1__r','LNCC_Axe_2__r','LNCC_DON_Axe_3__r','LNCC_Compte_Comptable_Cotisation_LU__r','LNCC_COTIS_Axe_1__r',
                                      'LNCC_COTIS_Axe_2__r','LNCC_COTIS_Axe_3__r','LNCC_VIVRE_Compte_Comptable__r','LNCC_VIVRE_Axe_1__r','LNCC_VIVRE_Axe_2__r',
                                      'LNCC_VIVRE_Axe_3__r','LNCC_VENTE_Compte_Comptable__r','LNCC_VENTE_Axe_1__r','LNCC_VENTE_Axe_2__r','LNCC_VENTE_Axe_3__r',
                                      'LNCC_PROD_ANNEXES_Compte_Comptable__r','LNCC_PROD_ANNEXES_Axe_1__r','LNCC_PROD_ANNEXES_Axe_2__r','LNCC_PROD_ANNEXES_Axe_3__r'])
                df['count_occurrence'] = df.groupby(['code','campagne_id'])['code'].transform('count')
                df = df.drop_duplicates(subset=['code','campagne_id'])
                offres = offre_obj.search([]).read(['code','code_campagne'])
                criteria_tuples = {(d['code'], d['code_campagne']) for d in offres}
                df_missing = df[df.apply(lambda x: (x['code'], x['campagne_id']) not in criteria_tuples and x['campagne_origine']=='SIEGE', axis=1)]
                df_update = df[df.apply(lambda x: (x['code'], x['campagne_id']) in criteria_tuples, axis=1)]
                missig_log_df = df_missing[['sf__id','code']].rename(columns={'code': 'name'})
                log_id = self.env['campagne.log'].create({'name':'Offres'})
                missig_log_df['log_id'] = log_id.id
                log_recs = missig_log_df.to_dict('records')
                self.env['campagne.log.line'].create(log_recs)
                self.update_offre(df_update,self.update)
        return {'type': 'ir.actions.act_window_close'} 