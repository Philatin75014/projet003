import sys
import os

# Ajouter le chemin du sous-répertoire `utils` où se trouve le fichier Python pur
sys.path.append(os.path.abspath('C:\\odoo\\projets\\custom\\maquette_data_003\\models\\utils'))

# Importer directement la fonction que vous souhaitez tester sans passer par les imports relatifs
from .datasource import get_param_canal_campagne_offre_data


def test_get_param_canal_campagne_offre_data(code_comite):
    try:
        records = get_param_canal_campagne_offre_data(code_comite)
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
    except Exception as e:
        print(f"Erreur lors de l'exécution du test : {e}")

# Exécution du test
if __name__ == "__main__":
    test_get_param_canal_campagne_offre_data('000')
