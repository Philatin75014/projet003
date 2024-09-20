import sys
import os

# Ajouter le chemin de `src` au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.traitement import traiter_donnees
from src.traitement import filtrer_donnees_par_code_comite  
from src.traitement import filtrer_offres_aiguillables  
from src.affichage import afficher_donnees
from src.datasource import lire_donnees_csv  # Pour le développement avec CSV
from src.datasource import execute_query  # Pour le développement avec BDD
from src.datasource import execute_querySQLAl    # Pour le développement avec BDD
from src.datasource import insert_row  # Pour le développement avec BDD
from src.datasource import insert_rowAlchemi  # Pour le développement avec BDD   
from src.datasource import executequery_oracle_sysmarlig  # Pour le développement avec BDD  
from src.utils import load_dotenv
from src.datasource import executequerySOQL  # Pour le développement avec BDD


if __name__ == "__main__":
    # Lire les données à partir d'un fichier CSV
    OffresSysmarlig = lire_donnees_csv('data/offres_sysmarlig.csv')
    OffresDonalig = lire_donnees_csv('data/offres_donalig.csv')
    #AiguillagesPortail = lire_donnees_csv('data/aiguillages_portail.csv')
    # Traiter les données
    #donnees_traitees = traiter_donnees(donnees)
    OffresSymarligFiltre = filtrer_donnees_par_code_comite(OffresSysmarlig,'069')
    OffresDonaligFiltre = filtrer_donnees_par_code_comite(OffresDonalig,'069')  
    #AiguillagesPortailFiltre = filtrer_donnees_par_code_comite(AiguillagesPortail,'069')
    AiguillagesPortailFiltre=execute_querySQLAl('075')
    #OffresAiguillables=filtrer_offres_aiguillables(OffresSymarligFiltre,AiguillagesPortailFiltre)
    OffresAiguillables=filtrer_offres_aiguillables(OffresDonalig,AiguillagesPortailFiltre)
    # Afficher les données
    #afficher_donnees(OffresSysmarligFiltre)
    afficher_donnees(AiguillagesPortailFiltre)
    afficher_donnees(OffresDonaligFiltre)
    print('offres totale du comité : ',len(OffresDonaligFiltre))
    print('Aiguillage déjà en place pour le comité : ',len(AiguillagesPortailFiltre))
    print('Offres aiguillables pour le comité : ',len(OffresAiguillables))
    afficher_donnees(AiguillagesPortailFiltre)
    #tentative d'insertion d'une ligne
    #insert_row({'TYPE_CANAL':'PAS','CODE_SOURCE':'PAZ','CODE_COMITE':'333','LIBELLE_OPERATION':'test','CODE_OPERATION_CAMPAGNE':'test','CODE_MISSION_OFFRE':'test','CODE_CAMPAGNE':'test','CODE_OFFRE':'test','DATE_DEBUT_OPE':'2024-01-01','DATE_FIN_OPE':'2024-09-30'})   
    #insert_rowAlchemi({'TYPE_CANAL':'PAS','CODE_SOURCE':'PAZ','CODE_COMITE':'075','LIBELLE_OPERATION':'test','CODE_OPERATION_CAMPAGNE':'test','CODE_MISSION_OFFRE':'test','CODE_CAMPAGNE':'test','CODE_OFFRE':'test','DATE_DEBUT_OPE':'2024-01-01','DATE_FIN_OPE':'2024-09-30'})   
    AiguillagesPortailFiltre=execute_querySQLAl('333')
    afficher_donnees(AiguillagesPortailFiltre)
    # Exemple d'utilisation
    executequery_oracle_sysmarlig('069')
    # Charger le fichier .env situé à la racine du projet

load_dotenv(dotenv_path='C:/TOM/.env')

# Accéder aux variables

#test_login_url = os.getenv('test_login_url')
#test_client_id = os.getenv('test_client_id')
#test_client_secret = os.getenv('test_client_secret')
#print(test_login_url)
#print(test_client_id)
#print(test_client_secret)
RequeteSOQL=executequerySOQL('069')
afficher_donnees(RequeteSOQL)

