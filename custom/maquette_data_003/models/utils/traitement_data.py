import pandas as pd

def traiter_donnees(donnees):
    """ Appliquer des transformations ou filtres sur les données """
    # Filtrer ou transformer les données si nécessaire
    donnees_filtrees = [donnee for donnee in donnees if donnee.get('CODE_COMITE') == '044']
    return donnees_filtrees  # Retourne les données filtrées

    #return donnees  # Retourne les données telles quelles pour l'instant

def filtrer_donnees_par_code_comite(donnees, code_comite):
    """Retourner une nouvelle liste filtrée sans modifier le dictionnaire original."""
    df = pd.DataFrame(donnees)
    # Afficher les noms de colonnes pour vérifier la présence de 'CODE_COMITE'
    #print("Noms des colonnes :", df.columns)
    
    # Afficher un échantillon des données pour vérifier la structure
    #print("Échantillon des données :", df.head())
    
    # Filtrer les données basées sur le code_comite
    df_filtre = df[df['CODE_COMITE'] == code_comite]    
    # Convertir le DataFrame filtré en liste de dictionnaires
    donnees_filtrees = df_filtre.to_dict(orient='records')
    
    return donnees_filtrees

def filtrer_offres_aiguillables(aiguillages_existants,offres):
    """Retourne la liste des offres n'ayant pas déjà un aiguillage"""
    
    # Créer des DataFrames à partir des offres et aiguillages existants
    dfOffres = pd.DataFrame(offres)
    dfAiguillages = pd.DataFrame(aiguillages_existants)

    # Vérifier si l'un des DataFrames est vide avant la fusion
    if dfOffres.empty:
        print("Le DataFrame des offres est vide")
        return offres  # Retourner les offres telles quelles si dfOffres est vide

    if dfAiguillages.empty:
        print("Le DataFrame des aiguillages existants est vide")
        return offres  # Retourner les offres si dfAiguillages est vide

    # Harmoniser la casse des colonnes (passer en majuscules pour tout uniformiser)
    dfOffres.rename(columns=str.upper, inplace=True)
    dfAiguillages.rename(columns=str.upper, inplace=True)

    # Effectuer une jointure externe uniquement sur les colonnes 'code_campagne' et 'code_offre'
    merged_df = pd.merge(dfOffres, dfAiguillages, on=['CODE_COMITE', 'CODE_CAMPAGNE', 'CODE_MISSION_OFFRE'], how='outer', indicator=True)

    # Filtrer les lignes présentes uniquement dans dfOffres (left_only)
    difference_df = merged_df[merged_df['_merge'] == 'left_only']

    # Ne conserver que les colonnes de dfOffres
    dfOffresAiguillables = difference_df[dfOffres.columns]

    # Convertir le DataFrame résultant en dictionnaire (liste de dictionnaires)
    resultat = dfOffresAiguillables.to_dict(orient='records')

    return resultat

    



