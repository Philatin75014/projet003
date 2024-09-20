import sys
import os

# Ajouter le chemin de `src` au PYTHONPATH
#sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append('C:/odoo/projets/custom/maquette_data_001/src')


# Importer la fonction depuis traitement.py
from traitement import traiter_donnees

# Tester l'importation et la fonction traiter_donnees
try:
    print("Importation de traitement réussie.")
    donnees = [{'Nom': 'Test1', 'Valeur': 100}, {'Nom': 'Test2', 'Valeur': 200}]
    donnees_traitees = traiter_donnees(donnees)
    print(donnees_traitees)
except ImportError as e:
    print(f"Erreur de traitement dans traitement : {e}")
