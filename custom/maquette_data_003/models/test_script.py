import utils.datasource
#from datasource import get_source_mpa_data


def test_get_source_mpa_data():
    # Appelle la fonction que tu veux tester
    result = utils.datasource.get_source_mpa_data()
    
    # Affiche les résultats
    print(result)

def test_get_source_list_offre_sysmarlig_data():
    # Appelle la fonction que tu veux tester
    result = utils.datasource.get_source_list_offre_sysmarlig_data("075")
    
    
    # Affiche les résultats
    print(result)

def test_get_source_donalig():
    # Appelle la fonction que tu veux tester
    result = utils.datasource.executequerySOQL("000")
    # Affiche les résultats
    print(result)

def test_get_source_sysmarlig():
    # Appelle la fonction que tu veux tester
    result = utils.datasource.executequery_oracle_sysmarlig("069")
    # Affiche les résultats
    print(result)

def test_get_comites_data():
    # Appelle la fonction que tu veux tester
    result = utils.datasource.get_comites_data()
    # Affiche les résultats
    print(result)

def test_get_source_list_offre_potentielles(code_comite):
    # Appelle la fonction que tu veux tester
    result = utils.datasource.get_source_list_offre_potentielles(code_comite)
    # Affiche les résultats
    print(result)



# Appelle la fonction de test
if __name__ == '__main__':
    #test_get_source_list_offre_sysmarlig_data()
    test_get_source_list_offre_potentielles("075")    
    #test_get_source_mpa_data()
    #test_get_source_donalig() 
    #test_get_source_sysmarlig()
    #test_get_comites_data()
