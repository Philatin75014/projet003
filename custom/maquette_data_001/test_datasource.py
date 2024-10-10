from odoo import api, SUPERUSER_ID
import odoo

def test_load_data_from_sql(env):
    """Test manuel pour la méthode load_data_from_sql avec des prints."""

    # Instancier le modèle 'param.canal.campagne.offre'
    ParamCanalCampagneOffre = env['param.canal.campagne.offre']

    # Appeler la méthode manuellement avec un code_comite factice
    print("Début du test: chargement des données depuis SQL pour le comité '000'")
    
    try:
        # Appel de la méthode load_data_from_sql
        ParamCanalCampagneOffre.load_data_from_sql('000')  # Utiliser le code_comite approprié
        print("Les données ont été chargées avec succès.")
        
        # Recherche des enregistrements créés pour vérifier les données
        records = ParamCanalCampagneOffre.search([('code_comite', '=', '000')])
        if records:
            print(f"{len(records)} enregistrements trouvés pour le comité '000'.")
            for record in records:
                print("Enregistrement :")
                print(f"Type Canal: {record.type_canal}")
                print(f"Code Source: {record.code_source}")
                print(f"Code Comité: {record.code_comite}")
                print(f"Libellé Opération: {record.libelle_operation}")
                print(f"Code Mission Offre: {record.code_mission_offre}")
                print(f"Code Campagne: {record.code_campagne}")
                print(f"Code Offre: {record.code_offre}")
                print(f"Date Début: {record.date_debut_ope}")
                print(f"Date Fin: {record.date_fin_ope}")
        else:
            print("Aucun enregistrement trouvé pour le comité '000'.")
    
    except Exception as e:
        print(f"Erreur lors du chargement des données : {str(e)}")

# Exécuter le test
if __name__ == "__main__":
    # Initialiser l'environnement Odoo
    odoo.tools.config.parse_config(['--database=test_db'])  # Remplacez 'test_db' par le nom de votre base de données de test
    with odoo.api.Environment.manage():
        registry = odoo.registry(odoo.tools.config['test_db'])
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            test_load_data_from_sql(env)
