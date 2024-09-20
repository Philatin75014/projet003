import sys
import os

# Ajouter le chemin de `src` au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
try:
    from src.datasource import lire_donnees_csv
    print("Importation de datasource réussie.")
except ImportError as e:
    print(f"Erreur d'importation dans datasource : {e}")
