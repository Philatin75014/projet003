def afficher_donnees(donnees):
    """ Affiche les données sous forme de liste """
    for i, donnee in enumerate(donnees, 1):
        #print(f"{i}. CODE_COMITE: {donnee['CODE_COMITE']} - COD_CAMPAGNE: {donnee['COD_CAMPAGNE']} - CODE_OFF: {donnee['CODE_OFF']} - OFF_LIBELLE: {donnee['OFF_LIBELLE']}")
        #print(f"{i}. {donnee}")
        valeurs = list(donnee.values())
        valeurs_str = ', '.join(map(str, valeurs))
        #print(f"{i}. {valeurs}")
        print(valeurs_str)
