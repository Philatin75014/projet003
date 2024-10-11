import sys
import os
import importlib.util

# Définir le chemin absolu du fichier `datasource.py`
module_path = 'C:\\odoo\\projets\\custom\\maquette_data_003\\models\\utils\\datasource.py'

# Charger le module `datasource` dynamiquement sans charger d'autres modules
spec = importlib.util.spec_from_file_location("datasource", module_path)
datasource = importlib.util.module_from_spec(spec)
spec.loader.exec_module(datasource)

# Test function
def test_get_param_canal_campagne_offre_data(code_comite):
    records = datasource.get_param_canal_campagne_offre_data(code_comite)

    # Afficher les résultats
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
