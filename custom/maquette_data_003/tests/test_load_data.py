# tests/test_load_data.py
import sys
import os
import importlib.util
# Ajoute le chemin vers le répertoire contenant le fichier à tester
#sys.path.append('C:\\odoo\\projets\\custom\\maquette_data_003\\models\\utils')
# Définir le chemin absolu du fichier `datasource.py`
module_path = 'C:\\odoo\\projets\\custom\\maquette_data_003\\models\\utils\\datasource.py'

# Charger le module dynamiquement
spec = importlib.util.spec_from_file_location("datasource", module_path)
datasource = importlib.util.module_from_spec(spec)
# Remplacer temporairement les imports relatifs par des imports absolus
with open(module_path, 'r') as file:
    module_code = file.read()
    module_code = module_code.replace('from .connexion_bdd import open_connection',
                                      'from maquette_data_003.models.utils.connexion_bdd import open_connection')

exec(module_code, datasource.__dict__)
#from models.utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
#from datasource import get_param_canal_campagne_offre_data


print("Le script commence à s'exécuter...")

#import pandas as pd
#import numpy as np
# Importez toute autre bibliothèque nécessaire

# Importer la fonction du module toto
#from paramcanalcampagneoffre import load_data_from_sql
#from maquette_data_003.models.paramcanalcampagneoffre import load_data_from_sql


"""""
def test_load_data_from_sql():
    # Appeler la fonction réelle
    records = load_data_from_sql('000')

    # Afficher les résultats de la fonction dans le test
    print("Données chargées pour le comité '000':")
    for record in records:
        print("Enregistrement :")
        print(f"Type Canal: {record.get('TYPE_CANAL')}")
        print(f"Code Source: {record.get('CODE_SOURCE')}")
        print(f"Code Comité: {record.get('CODE_COMITE')}")
        print(f"Libellé Opération: {record.get('LIBELLE_OPERATION')}")
        print(f"Code Mission Offre: {record.get('CODE_MISSION_OFFRE')}")
        print(f"Code Campagne: {record.get('CODE_CAMPAGNE')}")
        print(f"Code Offre: {record.get('CODE_OFFRE')}")
        print(f"Date Début: {record.get('DATE_DEBUT_OPE')}")
        print(f"Date Fin: {record.get('DATE_FIN_OPE')}")

"""

def test_get_param_canal_campagne_offre_data(code_comite):
    records = datasource.get_param_canal_campagne_offre_data(code_comite)
        
        # Créer des enregistrements dans le modèle à partir des données retournées
    for record in records:
        print(f"Type Canal: {record.get('TYPE_CANAL')}")
        print(f"Code Source: {record.get('CODE_SOURCE')}")
        print(f"Code Comité: {record.get('CODE_COMITE')}")
        print(f"Libellé Opération: {record.get('LIBELLE_OPERATION')}")
        print(f"Code Mission Offre: {record.get('CODE_MISSION_OFFRE')}")
        print(f"Code Campagne: {record.get('CODE_CAMPAGNE')}")
        print(f"Code Offre: {record.get('CODE_OFFRE')}")
        print(f"Date Début: {record.get('DATE_DEBUT_OPE')}")
        print(f"Date Fin: {record.get('DATE_FIN_OPE')}")
        print("-" * 40)  # Séparateur pour chaque enregistrement


# Exécution du test
if __name__ == "__main__":
    test_get_param_canal_campagne_offre_data('000')
