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

def filtrer_offres_aiguillables(offres,aiguillages_existants):
    """Retourne la liste des offres n''ayant pas deja un aiguillage""" 
    dfOffres = pd.DataFrame(offres) 
    dfAiguillages = pd.DataFrame(aiguillages_existants)
    # Effectuer une jointure externe uniquement sur les colonnes 'code_campagne' et 'code_offre'
    merged_df = pd.merge(dfOffres, dfAiguillages, on=['CODE_COMITE','CODE_CAMPAGNE', 'CODE_OFFRE'], how='outer', indicator=True)
    # Filtrer les lignes présentes uniquement dans df1 (left_only)
    difference_df = merged_df[merged_df['_merge'] == 'left_only']
    # Ne conserver que les colonnes de df1 (qui sont toutes les colonnes du dictionnaire d'origine)
    # Cela évite de renvoyer les colonnes inutiles comme '_merge' ou celles de df2.
    dfOffresAiguillables = difference_df[dfOffres.columns]
        # Convertir le DataFrame résultant en dictionnaire (liste de dictionnaires)
    resultat = dfOffresAiguillables.to_dict(orient='records')

    return resultat
    



