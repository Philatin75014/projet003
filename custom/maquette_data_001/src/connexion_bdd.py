import pyodbc
import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from utils import sf_api

def open_connection():
# Récupérer le mot de passe depuis la variable d'environnement
    password = os.getenv('SQLSERVER_TEST_PASSWORD')

    if password:
        print("Mot de passe récupéré avec succès.")
    else:
        print("Erreur : Mot de passe non défini dans les variables d'environnement.")
    # Paramètres de connexion
    server = 'TST-SVV048'  # ou 'localhost' si en local
    database = 'GESFLUXTEST'
    username = 'USER_PYTHON_TEST'

    # Chaîne de connexion à SQL Server
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # Établir la connexion
    conn = pyodbc.connect(conn_str)
    return conn

# Fonction pour ouvrir la connexion à SQL Server avec SQLAlchemy
def open_sqlalchemy_connectionGESFLUX():
  # Récupérer le mot de passe depuis la variable d'environnement
    password = os.getenv('SQLSERVER_TEST_PASSWORD')

    if password:
        print("Mot de passe récupéré avec succès.")
    else:
        print("Erreur : Mot de passe non défini dans les variables d'environnement.")
  
    # Paramètres de connexion
    server = 'TST-SVV048'  # ou 'localhost' si en local
    database = 'GESFLUXTEST'
    username = 'USER_PYTHON_TEST'
    # Échapper les espaces et caractères spéciaux dans le nom du driver ODBC
    driver = 'ODBC Driver 17 for SQL Server'
    driver_escaped = urllib.parse.quote_plus(driver)

    # Créer l'URL de connexion manuellement avec pyodbc
    connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # Utiliser l'objet URL de SQLAlchemy pour générer la connexion
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    # Créer le moteur SQLAlchemy avec l'URL personnalisée
    engine = create_engine(connection_url)
    # Chaîne de connexion via SQLAlchemy
    #connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL+Server'
    #connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver_escaped}"
    #engine = create_engine(connection_string)
    
    return engine

# Fonction pour ouvrir la connexion Oracle via SQLAlchemy
def open_oracle_connectionSYSMARLIG():
      # Récupérer le mot de passe depuis la variable d'environnement
    password = os.getenv('ORACLE_TEST_PASSWORD')

    if password:
        print("Mot de passe récupéré avec succès.")
    else:
        print("Erreur : Mot de passe non défini dans les variables d'environnement.")
    username = 'SYSMARLIG'
    host = '172.18.10.35'  # Par exemple : 'localhost' ou une IP
    port = '1521'  # Port par défaut pour Oracle
    service_name = 'FED'  # Ou SID selon la configuration

    # Créer la chaîne de connexion SQLAlchemy pour Oracle
    connection_string = f'oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}'
    
    # Créer le moteur SQLAlchemy
    engine = create_engine(connection_string)
    return engine

def open_saleforce_connectionDONALIG():
    # Pour l'environnement de test
    salesforce_api = sf_api()
    return salesforce_api