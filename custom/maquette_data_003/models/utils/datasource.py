import sys
import os
# Ajouter le répertoire courant au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import csv
import pandas as pd
#import simple_salesforce
from sqlalchemy import text
from .connexion_bdd import open_connection
from .connexion_bdd import open_sqlalchemy_connectionGESFLUX
from .connexion_bdd import open_oracle_connectionSYSMARLIG
from .connexion_bdd import open_saleforce_connectionDONALIG
from .traitement_data import filtrer_donnees_par_code_comite
from .traitement_data import filtrer_offres_aiguillables

def lire_donnees_csv(fichier_csv):
    """ Lire des données à partir d'un fichier CSV """
    with open(fichier_csv, mode='r', encoding='utf-8-sig') as fichier:
        lecteur_csv = csv.DictReader(fichier,delimiter=';')
        return list(lecteur_csv)

# Fonction pour exécuter une requête paramétrée
def execute_query(code_comite):
     
    query = '''
    SELECT [TYPE_CANAL]  
    ,[CODE_SOURCE]  
    ,[CODE_COMITE]  
    ,[LIBELLE_OPERATION]  
    ,[CODE_OPERATION_CAMPAGNE]  
    ,[CODE_MISSION_OFFRE]  
    ,[CODE_CAMPAGNE]  
    ,[CODE_OFFRE]  
    ,[DATE_DEBUT_OPE]  
    ,[DATE_FIN_OPE]  
    FROM [PWS].[PARAM_CANAL_CAMPAGNE_OFFRE]  
    where code_comite =?
    '''
    conn = open_connection()
    try:
        # Exécuter la requête avec pandas et le paramètre passé
        df = pd.read_sql(query, conn, params=[code_comite])
        # Convertir le DataFrame en dictionnaire
        return df.to_dict(orient='records')

    finally:
        # Toujours fermer la connexion, même en cas d'erreur
        conn.close()
# Fonction pour exécuter une requête paramétrée
def get_param_canal_campagne_offre_data(code_comite):
    # Requête SQL avec paramètre nommé :code_comite
    if code_comite=='000':  
        query = '''
    SELECT [TYPE_CANAL], [CODE_SOURCE], [CODE_COMITE], [LIBELLE_OPERATION],
           [CODE_OPERATION_CAMPAGNE], [CODE_MISSION_OFFRE], [CODE_CAMPAGNE],
           [CODE_OFFRE], [DATE_DEBUT_OPE], [DATE_FIN_OPE]
    FROM [PWS].[PARAM_CANAL_CAMPAGNE_OFFRE]
    WHERE   
    [TYPE_CANAL] = 'PAS' order by DATE_FIN_OPE desc 
     '''
    else :    
        query = '''
    SELECT [TYPE_CANAL], [CODE_SOURCE], [CODE_COMITE], [LIBELLE_OPERATION],
           [CODE_OPERATION_CAMPAGNE], [CODE_MISSION_OFFRE], [CODE_CAMPAGNE],
           [CODE_OFFRE], [DATE_DEBUT_OPE], [DATE_FIN_OPE]
    FROM [PWS].[PARAM_CANAL_CAMPAGNE_OFFRE]
    WHERE 
    [TYPE_CANAL] = 'PAS' AND
    [CODE_COMITE] = :code_comite order by DATE_FIN_OPE desc 
    '''
    
    # Ouvrir une connexion SQLAlchemy
    engine = open_sqlalchemy_connectionGESFLUX()
  
    # Utiliser un bloc `with` pour gérer la connexion proprement
    with engine.connect() as conn:
        # Exécuter la requête avec pandas et le paramètre nommé
        df = pd.read_sql(text(query), conn, params={"code_comite": code_comite})

    # Convertir le DataFrame en dictionnaire
    return df.to_dict(orient='records')

def get_source_mpa_data():
    query = '''
    SELECT CODE_SOURCE, LIBELLE_SOURCE
    FROM PWS.SOURCE_MPA WHERE CODe_SOURCE LIKE 'P%'
    '''
    # Connexion SQLAlchemy à ta base de données SQL Server (ou une autre source)
    engine = open_sqlalchemy_connectionGESFLUX()

    # Utiliser un bloc with pour gérer proprement la connexion
    with engine.connect() as conn:
        # Exécuter la requête avec pandas
        df = pd.read_sql(query, conn)

    # Retourner les données sous forme de dictionnaire
    return df.to_dict(orient='records')

def get_source_list_offre_potentielles(code_comite):
    #futur routage on cherche dans donalig ou sysmarlig
    #pour le moment uniquement sysmarlig
    #on va charger la liste dans la base sysmarlig
    Aiguillages_existants_comite =get_param_canal_campagne_offre_data(code_comite)
    print(Aiguillages_existants_comite)
    Offres_potentielles_comite = get_source_list_offre_sysmarlig_data(code_comite)
    print(Offres_potentielles_comite)
    return filtrer_offres_aiguillables(Aiguillages_existants_comite,Offres_potentielles_comite)


def get_source_list_offre_sysmarlig_data(code_comite):
    query = '''
    SELECT  
        code_comite as CODE_COMITE,
        cod_campagne as CODE_CAMPAGNE,
        code_off as CODE_MISSION_OFFRE,
        off_libelle,
        cod_campagne || ' ' || code_off || ' ' || off_libelle AS libelle_total
    FROM offre  
    WHERE cod_campagne LIKE '%BFP800'  
    AND CODE_OFF LIKE 'E0D%' 
    AND code_comite = :code_comite
    ORDER BY cod_campagne DESC
    '''
    
    # Connexion à la base Oracle via SQLAlchemy
    engine = open_oracle_connectionSYSMARLIG()

    # Utiliser un bloc with pour gérer proprement la connexion
    with engine.connect() as conn:
        # Exécuter la requête en utilisant la méthode `text` pour Oracle
        df = pd.read_sql(text(query), conn, params={"code_comite": code_comite})

    # Retourner les données sous forme de dictionnaire
    return df.to_dict(orient='records')




def get_comites_data():
    query = '''
    SELECT 
    CODE_COMITE,
    NOM,
    CODE_COMITE+' '+NOM AS CODE_COMITE_NOM,
    CASE 
        WHEN IS_MIG_DONALIG = 1 THEN 'DONALIG'
        ELSE 'SYSMARLIG'
    END AS 'CIBLE',
    ISNULL(FORMAT(DATA_MIG_DONALIG, 'dd/MM/yyyy'), 'NON') AS 'DATE_MIGRATION_DONALIG'
FROM 
    PWS.COMITE
ORDER BY 
    CODE_COMITE;

    '''
    # Connexion SQLAlchemy à ta base de données SQL Server (ou une autre source)
    engine = open_sqlalchemy_connectionGESFLUX()

    # Utiliser un bloc with pour gérer proprement la connexion
    with engine.connect() as conn:
        # Exécuter la requête avec pandas
        df = pd.read_sql(query, conn)

    # Retourner les données sous forme de dictionnaire
    return df.to_dict(orient='records')



# Fonction pour insérer une ligne dans la table SQL via sqlalchemy
def insert_rowAlchemi(data):
     # Convertir les dates en format datetime dans le dictionnaire
    #data['DATE_DEBUT_OPE'] = pd.to_datetime(data['DATE_DEBUT_OPE'])
    #data['DATE_FIN_OPE'] = pd.to_datetime(data['DATE_FIN_OPE'])
    # Convertir les données (dictionnaire) en DataFrame
    df = pd.DataFrame([data])  # Créer un DataFrame à partir du dictionnaire

    # Ouvrir une connexion SQLAlchemy
    engine = open_sqlalchemy_connectionGESFLUX()

   # Insérer les données dans la table SQL avec gestion manuelle de la transaction
    with engine.connect() as connection:
        trans = connection.begin()  # Démarre une transaction manuelle
        try:
            df.to_sql('PARAM_CANAL_CAMPAGNE_OFFRE', con=connection, schema='PWS', if_exists='append', index=False)
            trans.commit()  # Valide la transaction
            print("Insertion réussie")
        except Exception as e:
            trans.rollback()  # Annule la transaction en cas d'erreur
            print(f"Erreur lors de l'insertion : {e}")

# Fonction pour insérer une ligne dans la table SQL via pyodbc
def insert_row(data):
    # Ouvrir la connexion
    conn = open_connection()
    cursor = conn.cursor()

    # Générer dynamiquement la requête d'insertion
    table_name = 'PWS.PARAM_CANAL_CAMPAGNE_OFFRE'
    columns = ', '.join(data.keys())  # Créer une chaîne avec les colonnes
    placeholders = ', '.join(['?'] * len(data))  # Générer des placeholders pour les valeurs
    values = tuple(data.values())  # Extraire les valeurs du dictionnaire

    query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

    try:
        # Exécuter la requête
        cursor.execute(query, values)
        conn.commit()  # Valider l'insertion
        print("Ligne insérée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'insertion : {e}")
        conn.rollback()  # Annuler en cas d'erreur
    finally:
        # Toujours fermer la connexion
        cursor.close()
        conn.close()
def executequery_oracle_sysmarlig(code_comite):
# Exemple d'utilisation
    engine = open_oracle_connectionSYSMARLIG()

    # Exécuter une requête simple pour vérifier la connexion
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM COMITE WHERE CODE_COMITE = :code_comite"), {"code_comite": code_comite})
        #result = conn.execute(text("SELECT * FROM COMITE "))
    for row in result:
        print(row)

def executequerySOQL(code_comite):
    # Exemple d'une requête SOQL pour récupérer des comptes
    #query = "SELECT Id, Name FROM Account LIMIT 10"
    #" AND  ParentId in ('7017Q000000l8N6QAI','7017Q0000005QChQAM')"
    #LNCC_Comites_participants__c, LNCC_Comites_participants2__c,
    query = """
    SELECT Id, RecordType.Name, 
           Name, LNCC_Code_Campagne__c, LNCC_Code_offre__c, Label_Offre__c, IsActive
    FROM Campaign
    WHERE (LNCC_Comites_participants__c INCLUDES ('CD069') 
           OR LNCC_Comites_participants2__c INCLUDES ('CD069'))
           AND ParentId IN ('7017Q000000l8N6QAI', '7017Q0000005QChQAM')
    ORDER BY Label_Offre__c
    """
    salesforce_api=open_saleforce_connectionDONALIG()
    result = salesforce_api.sf.query(query)
   # Vérifier s'il y a des enregistrements, sinon retourner une liste vide
    if 'records' in result and result['records']:
        return result['records']  # On retourne les enregistrements s'ils existent
    else:
        return []  # Retourne une liste vide s'il n'y a aucun résultat
