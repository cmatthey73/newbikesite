# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 17:22:39 2019

@author: chris
"""

####### Importations GARMIN - VERIFIER LES DATES

def import_garmin(garm_csv):
    import pandas as pd
    import sqlite3
    import datetime
    import numpy as np

    # garm_csv="Activities_13022022.csv"
    df = pd.read_csv("C:/Users/chris/Documents/"+garm_csv, header=0, sep=",")
    df.columns=df.columns.str.replace(" ","_") # suppression espaces !
    df.columns
    df.dtypes
    
    # Traitement changement de noms permanents pour certaines colonnes
    df.rename(columns={"Ascension_totale": "Gain_alt"}, inplace=True)
        
    # Traitement des potentielles colonnes manquantes
    col_mis=["Fréquence_cardiaque_moyenne", "Fréquence_cardiaque_maximale", "Distance", "Gain_alt"]
    for c in col_mis:
        if c not in df.columns:
           df[c]=None

    # Transformation champ Gain_alt
    df["Gain_alt"]=df["Gain_alt"].apply(str).str.replace(",","")

    # Transformation champ Date
    df["Date"]=pd.to_datetime(df["Date"], yearfirst=True) 
    df=df.sort_values(by=["Date"], ascending=True)
    df["Date"]=df["Date"].map(lambda x: x.date()) 
    df.dtypes
    
    # Transformation champ Temps (Timedelta)
    #df["Temps"]=pd.to_timedelta(df["Temps"])/datetime.timedelta(microseconds=1)
    df["Temps"]=pd.to_timedelta(df["Durée"])/datetime.timedelta(microseconds=1) # changement du nom du champ dans Garmin (juillet 2019) !
    df.dtypes

    # Traitement valeurs -- 
    def rplc(v):
        if v == "--":
            return(None)
        else:
            return(v)
            
    df=df.applymap(lambda x: rplc(x))
    df.dtypes

    # Transformation champs FC
    df[["Fréquence_cardiaque_moyenne", "Fréquence_cardiaque_maximale"]]=df[["Fréquence_cardiaque_moyenne",
      "Fréquence_cardiaque_maximale"]].applymap(lambda x: float(x) if x is not None else None) 
    # 30.04.2022 : à vérifier au prochain import !

    # 3.2. Chargement base de données
    
    conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
    query = "SELECT * FROM biketours_perfo"
    df_DB = pd.read_sql_query(query, conn)
    conn.close()
    
    dt_max=max(pd.to_datetime(df_DB["Date"]))
    df=df[df["Date"]>dt_max.date()]
    df.dtypes
    df_DB.dtypes

    # Création Refparcours_id et affectation tour selon DB si 1 seule variante
    conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
    query = "SELECT b.id, b.Parcours, b.Variante, c.Type FROM biketours_BikeTour b LEFT JOIN biketours_type c on b.type_id = c.id"
    tours_DB = pd.read_sql_query(query, conn)
    conn.close()

    # ------------ cas HT et CAP
    df.loc[(df["Type_d'activité"].str.upper().isin (["INDOOR_CYCLING", "VELO D'INTERIEUR"])) & (df["Titre"].str.upper() == "SPINNING"),"Refparcours_id"]=tours_DB.loc[(tours_DB["Parcours"].str.upper() == "SPINNING") ,"id"].iloc[0] 
    df.loc[(df["Type_d'activité"].str.upper().isin (["INDOOR_CYCLING", "VELO D'INTERIEUR"])) & (df["Titre"].str.upper() != "SPINNING"),"Refparcours_id"]=tours_DB.loc[(tours_DB["Parcours"].str.upper() == "HOMETRAINER") ,"id"].iloc[0] 
    df.loc[(df["Type_d'activité"].str.upper().str.match(r"(^COURSE.+PIED|^TRAIL|.+_RUNNING$)")) ,"Refparcours_id"]=tours_DB.loc[(tours_DB["Type"] == "cap" ) ,"id"].iloc[0] 
    # valeur None pour Vitesse max si course ou hometrainer 
    df.loc[(df["Type_d'activité"].str.upper().str.match(r"(^COURSE.+PIED|^TRAIL|.+_RUNNING$)")) ,"Vitesse_max"]=None
    df.loc[(df["Type_d'activité"].str.upper().isin (["INDOOR_CYCLING", "VELO D'INTERIEUR"])),"Vitesse_max"]=None
        
    df["Refparcours_id"].value_counts(dropna=False)

    # ------------ cas VTT et ROUTE : attribution directe si 1 seule variante
    uniques=tours_DB.groupby(["Parcours"])["Variante"].count()
    uniques=uniques[uniques<=1]
        
    catGAR=["mountain_biking","VTT","road_biking", "Cyclisme sur route"]
    typeDB=["vtt","vtt","route","route"]
    lst=zip(catGAR, typeDB)

    for gar, db in lst:
        ref=tours_DB.loc[(tours_DB["Type"]==db) & (tours_DB["Parcours"].isin(uniques.index.tolist())) , :]
        default=tours_DB.loc[tours_DB["Parcours"].str.match(db+"_\?"),"id"]
        print(default)
        for t in ref.itertuples(index=False):
    #        print(t)
    #        print(t.Parcours)
            df.loc[(df["Type_d'activité"]==gar) & (df["Titre"]==t.Parcours), "Refparcours_id"]=t.id
        df.loc[(df["Type_d'activité"]==gar) & (pd.isnull(df["Refparcours_id"])), "Refparcours_id"]=default.iloc[0] 
        #pas ok car default = Series => extraire chiffre
    
    # ------------ cas non traité ailleurs => cas ?_?
    default=tours_DB.loc[tours_DB["Parcours"].str.match("\?_\?"),"id"]
    df.loc[pd.isnull(df["Refparcours_id"]), "Refparcours_id"]=default.iloc[0]
        
    df["Refparcours_id"].value_counts(dropna=False)
    
    # Chargement
    
    # col_acc=df.columns.tolist()

    # =============================================================================
    # ["Type_d'activité",
    #  'Date',
    #  'Favori',
    #  'Titre',
    #  'Distance',
    #  'Calories',
    #  'Temps',
    #  'Fréquence_cardiaque_moyenne',
    #  'Fréquence_cardiaque_maximale',
    #  'Vitesse_moyenne',
    #  'Vitesse_max',
    #  'Gain_alt',
    #  "Perte_d'altitude",
    #  'Longueur_moyenne_des_foulées',
    #  'Rapport_vertical_moyen',
    #  'Oscillation_verticale_moyenne',
    #  'Training_Stress_Score®_(TSS®)',
    #  'Difficulté',
    #  'Constance',
    #  'Tps_au_fond',
    #  'Température_minimale',
    #  'Intervalle_à_la_surface',
    #  'Décompression',
    #  'Temps_du_meilleur_circuit',
    #  'Nombre_de_courses',
    #  'Température_maximale']
    # =============================================================================
    
    # col_DB=df_DB.columns.tolist()

    # =============================================================================
    # ['id',
    #  'Date',
    #  'Distance',
    #  'Temps',
    #  'Remarques',
    #  'Dénivelé',
    #  'Vitesse_max',
    #  'FC_moy',
    #  'FC_max',
    #  'Temps_part_1',
    #  'Temps_part_2',
    #  'Temps_part_3',
    #  'Temps_part_4',
    #  'Temps_part_5',
    #  'Temps_part_6',
    #  'Temps_part_7',
    #  'Temps_part_8',
    #  'Temps_part_9',
    #  'Temps_part_10',
    #  'Refparcours_id']
    # =============================================================================

    def create_perfGARMIN(conn, perf):
        # NB : FC_moy et FC_max n'ont jamais été renseignés !
        sql = ''' INSERT INTO biketours_perfo(Date,
                                              Distance,
                                              Temps,
                                              Remarques,
                                              Dénivelé,
                                              Vitesse_max,
                                              FC_moy,
                                              FC_max,
                                              Refparcours_id
                                              )'''+" VALUES"+"("+"?,"*8+"?"+")"
        cur = conn.cursor()
        cur.execute(sql, perf)
            #perf doit être un tuple avec 15 variables !

    # ordre lst_col doit correspondre à celui donnée dans create_perf
    lst_col=["Date",
             "Distance",
             "Temps",
             "Titre",
             "Gain_alt",
             "Vitesse_max",
             "Fréquence_cardiaque_moyenne",
             "Fréquence_cardiaque_maximale",
             "Refparcours_id"]

    # =============================================================================
    # ["Type_d'activité",
    #  'Date',
    #  'Favori',
    #  'Titre',
    #  'Distance',
    #  'Calories',
    #  'Temps',
    #  'Fréquence_cardiaque_moyenne',
    #  'Fréquence_cardiaque_maximale',
    #  'Vitesse_moyenne',
    #  'Vitesse_max',
    #  'Gain_alt',
    #  "Perte_d'altitude",
    #  'Longueur_moyenne_des_foulées',
    #  'Rapport_vertical_moyen',
    #  'Oscillation_verticale_moyenne',
    #  'Training_Stress_Score®_(TSS®)',
    #  'Difficulté',
    #  'Constance',
    #  'Tps_au_fond',
    #  'Température_minimale',
    #  'Intervalle_à_la_surface',
    #  'Décompression',
    #  'Temps_du_meilleur_circuit',
    #  'Nombre_de_courses',
    #  'Température_maximale']
    # =============================================================================


    conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
    
    for i in df[lst_col].itertuples(index=False):
        print(i)
        create_perfGARMIN(conn, i)
        conn.commit()
    
    conn.close()

#import_garmin("C:/Users/chris/Documents/Activities_15082019.csv")

#import_garmin("Activities_03092019.csv")
