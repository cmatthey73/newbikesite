# -*- coding: utf-8 -*-
"""
Created on Mon Ap_part22 09:58:17 2019

@author: chris
"""

### Objectif : peupler la DB d'exemples (si possible reprise données DB Access pour les tours et les perfos)

# Tables :
# biketours_buts = id, But, Descriptif
# biketours_type = id, Type, Descriptif
# biketours_biketour = id, Parcours, Variante, Descriptif, Nom_part_1, Dist_part_1 , Deniv_part_1, ... , 
#                      Nom_part_10, Dist_part_10 , Deniv_part_10, But_id (id But), Type_id (id Type)
# biketours_perfo = id, Date, Distance, Temps, Vitesse_max, FC_moy, FC_max, Temp_part_1, ... Temp_part_10, Refparcours_id (id biketours_biketour)

# 1. Créer les biketours_but et les biketours_types

import pandas as pd
import sqlite3

ex_buts = [("entrainement","entrainement simple"), ("course","course organisée")]
ex_type = [("vtt","vélo tout terrain"), ("route","vélo de route"), ("ht","home trainer"), ("cap", "course à pied")]

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")

def create_but(conn, but):
    sql = ''' INSERT INTO biketours_but(But, Descriptif)
                 VALUES(?,?) ''' # les ? ? seront remplacées par les valeurs données dans execute
                                 # les triple quote permettent d'écrire le texte sur plusieurs lignes !
    cur = conn.cursor()
    cur.execute(sql, but)
#    cur.executemany('INSERT INTO biketours_but(But, Descriptif) VALUES (?,?,?,?)', but) 
        # variante pour multiples insertions ! but doit être une liste de tuples (cf ex_buts)
    return cur.lastrowid # renvoie l'id (! no de ligne !)

def create_type(conn, type):
    sql = ''' INSERT INTO biketours_type(Type, Descriptif)
                 VALUES(?,?) ''' # les ? ? seront remplacées par les valeurs données dans execute
    cur = conn.cursor()
    cur.execute(sql, type)
    return cur.lastrowid # renvoie l'id (! no de ligne !)

for i in ex_buts:
    create_but(conn, i)
    conn.commit()

for i in ex_type:
    create_type(conn, i)
    conn.commit()

conn.close()

# Check 

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")

query = "SELECT * FROM biketours_type"
df = pd.read_sql_query(query, conn)
print(df)

query = "SELECT * FROM biketours_but"
df = pd.read_sql_query(query, conn)
print(df)

conn.close()

# 2. Créer les biketours_biketour (! liés à buts par But_id et types par Type_id)

import pandas as pd
import sqlite3

df = pd.read_csv("C:/Users/chris/Documents/Tours.txt", header=0, sep=";")
df.columns=df.columns.str.replace(" ","_") # suppression espaces !
df.columns

print(df["Type"].unique())
print(df["But"].unique())

# 2.1. Recodages Type et But

df.loc[df["Type"].str.upper()=="ROUTE","Type_adapt"]=2
df.loc[df["Type"].str.upper()=="VTT","Type_adapt"]=1
df.loc[(df["Type"].str.upper() == "HT/CAP") & (df["Parcours"] == "Hometrainer") ,"Type_adapt"]=3
df.loc[(df["Type"].str.upper() == "HT/CAP") & (df["Parcours"] == "Spinning") ,"Type_adapt"]=3
df.loc[(df["Type"].str.upper() == "HT/CAP") & (df["Parcours"] == "CourseAPied") ,"Type_adapt"]=4
df["Type"]=df["Type_adapt"]

df.loc[df["But"].str.upper()=="ENTRAÎNEMENT","But_adapt"]=1
df.loc[df["But"].str.upper()=="COURSE","But_adapt"]=2
df["But"]=df["But_adapt"]
df=df.drop(["Type_adapt", "Refparcours", "But_adapt"], axis=1)

# check comptage

c=0
count={}
for i in df["Type"]:
    if i in count:
        count[i]=count[i]+1
    else:   
        count[i]=1

print(count)

c=0
count={}
for i in df["But"]:
    if i in count:
        count[i]=count[i]+1
    else:   
        count[i]=1

print(count)

# 2.2. Chargement base de données

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
query = "SELECT * FROM biketours_biketour"
df_DB = pd.read_sql_query(query, conn)
conn.close()

col_acc=df.columns.tolist()

# =============================================================================
# ['Refparcours',
#  'Parcours',
#  'Variante',
#  'But',
#  'Type',
#  'Descriptif_général',
#  'Distance_partielle_1',
#  'Dénivelé_partiel_1',
#  'Détail_partiel_1',
#  'Distance_partielle_2',
#  'Dénivelé_partiel_2',
#  'Détail_partiel_2',
#  'Distance_partielle_3',
#  'Dénivelé_partiel_3',
#  'Détail_partiel_3',
#  'Distance_partielle_4',
#  'Dénivelé_partiel_4',
#  'Détail_partiel_4',
#  'Distance_partielle_5',
#  'Détail_partiel_5',
#  'Dénivelé_partiel_5',
#  'Distance_partielle_6',
#  'Dénivelé_partiel_6',
#  'Détail_partiel_6',
#  'Distance_partielle_7',
#  'Dénivelé_partiel_7',
#  'Détail_partiel_7',
#  'Distance_partielle_8',
#  'Dénivelé_partiel_8',
#  'Détail_partiel_8']
# =============================================================================

col_DB=df_DB.columns.tolist()

# =============================================================================
# ['id',
#  'Parcours',
#  'Variante',
#  'Descriptif',
#  'Descr_part_1',
#  'Dist_part_1',
#  'Deniv_part_1',
#  'Descr_part_2',
#  'Dist_part_2',
#  'Deniv_part_2',
#  'Descr_part_3',
#  'Dist_part_3',
#  'Deniv_part_3',
#  'Descr_part_4',
#  'Dist_part_4',
#  'Deniv_part_4',
#  'Descr_part_5',
#  'Dist_part_5',
#  'Deniv_part_5',
#  'Descr_part_6',
#  'Dist_part_6',
#  'Deniv_part_6',
#  'Descr_part_7',
#  'Dist_part_7',
#  'Deniv_part_7',
#  'Descr_part_8',
#  'Dist_part_8',
#  'Deniv_part_8',
#  'Dist_part_9',
#  'Deniv_part_9',
#  'Descr_part_10',
#  'Dist_part_10',
#  'Deniv_part_10',
#  'But_id',
#  'Type_id',
#  'Descr_part_9']
# 
# =============================================================================

def create_tour(conn, tour):
    sql = ''' INSERT INTO biketours_biketour( Parcours,
                                              Variante,
                                              But_id,
                                              Type_id,
                                              Descriptif,
                                              Descr_part_1,
                                              Dist_part_1,
                                              Deniv_part_1,
                                              Descr_part_2,
                                              Dist_part_2,
                                              Deniv_part_2,
                                              Descr_part_3,
                                              Dist_part_3,
                                              Deniv_part_3,
                                              Descr_part_4,
                                              Dist_part_4,
                                              Deniv_part_4,
                                              Descr_part_5,
                                              Dist_part_5,
                                              Deniv_part_5,
                                              Descr_part_6,
                                              Dist_part_6,
                                              Deniv_part_6,
                                              Descr_part_7,
                                              Dist_part_7,
                                              Deniv_part_7,
                                              Descr_part_8,
                                              Dist_part_8,
                                              Deniv_part_8
                                              )'''+" VALUES"+"("+"?,"*28+"?"+")"
    cur = conn.cursor()
    cur.execute(sql, tour)
        #tour doi être un tuple avec 29 variables !

# ordre lst_col doit correspondre à celui donnée dans create_tour
lst_col=['Parcours',
          'Variante',
          'But',
          'Type',
          'Descriptif_général',
          'Détail_partiel_1',
          'Distance_partielle_1',
          'Dénivelé_partiel_1',
          'Détail_partiel_2',
          'Distance_partielle_2',
          'Dénivelé_partiel_2',
          'Détail_partiel_3',
          'Distance_partielle_3',
          'Dénivelé_partiel_3',
          'Détail_partiel_4',
          'Distance_partielle_4',
          'Dénivelé_partiel_4',
          'Détail_partiel_5',
          'Distance_partielle_5',
          'Dénivelé_partiel_5',
          'Détail_partiel_6',
          'Distance_partielle_6',
          'Dénivelé_partiel_6',
          'Détail_partiel_7',
          'Distance_partielle_7',
          'Dénivelé_partiel_7',
          'Détail_partiel_8',
          'Distance_partielle_8',
          'Dénivelé_partiel_8']

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")

for i in df[lst_col].itertuples(index=False):
    create_tour(conn, i)
    conn.commit()

conn.close()

# Tours factices pour tours non alloués

def create_fact(conn, tour):
    sql = ''' INSERT INTO biketours_biketour(Parcours,
                                              But_id,
                                              Type_id
                                              ) VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, tour)

factices=[("vtt_?",1, 1),
          ("route_?", 1, 2)]

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
for i in factices:
    create_fact(conn, i)
    conn.commit()

conn.close()

# 3. Créer les biketours_perfo (! liés à biketour par Refparcours_id) 
## OK FONCTIONNE MAIS PROBLEME DANS DB ACCESS AVEC TOUR NO 27 QUI N'EXISTE PAS => TRANSFORMER >= 27 EN 27+1 

import pandas as pd
import sqlite3
import datetime
#import numpy as np

df = pd.read_csv("C:/Users/chris/Documents/Perfo.txt", header=0, sep=";")
df.columns=df.columns.str.replace(" ","_") # suppression espaces !
df.columns

## Correction problème DB access : tour no 27 existe pas => adapter ref dans Perfo si >=28, faire -1
df.loc[df["Refparcours"]>=28,"Refparcours"]=df.loc[df["Refparcours"]>=28,"Refparcours"]-1
df["Refparcours"].unique()

# 2.1. Traitement champs Date et Temps  DATES A REVOIR ---- PROBLEMES

## ! Critère = voir ce qui est supporté par SQL-lite, a priori uniquement :
## SQLite type	Python type
## NULL        None
## INTEGER	  int or long, depending on size
## REAL	     float
## TEXT	     depends on text_factory, unicode by default
## BLOB	     buffer
## MAIS SQL - lite peut gérer :
## SQLite3 comes with support of DATE and TIMESTAMP (datetime) types (see dbapi2.py). 
## The DATE field accepts a string in ISO 8601 format 'YYYY-MM-DD' or datetime.date object
## The TIMESTAMP field accepts a string in ISO 8601 format 'YYYY-MM-DD HH:MM:SS.mmmmmm' or datetime.datetime object:
    
# le champ DateField dans Django a besoin d'objets datetime.date 
df["Date"]=pd.to_datetime(df["Date"], dayfirst = True) 
df["Date"]=df["Date"].map(lambda x: x.date()) 
df=df.sort_values(by=['Date'], ascending=True)
df.dtypes
## le champ DurationField dans Django a besoin d'objets datetime.timedelta
## DurationField = un champ pour stocker des périodes de temps, représentées en Python par des objets timedelta. 
## Avec PostgreSQL, le type de données utilisé est un interval et avec Oracle, le type de données est INTERVAL DAY(9) TO SECOND(6). 
## Sinon, c’est un grand nombre entier bigint de microsecondes qui est utilisé => C'EST LE CAS !!
## timedelta.total_seconds()
## Return the total number of seconds contained in the duration. 
## Equivalent to td / timedelta(seconds=1). For interval units other than seconds, use the division form directly (e.g. td / timedelta(microseconds=1)).
col_tmp=df.columns[df.columns.str.match(r"Temps(_partiel_){0,1}\d{0,1}$") ]
def extr_duration(s):
    extr=str(s).split(" ")
    if len(extr) == 1:
        return(None) # optimal ??? pour éviter les NaT qui posent problèmes
    else :
       return(float(pd.to_timedelta(extr[1])/datetime.timedelta(microseconds=1)))
       # transformation en float sinon problème à l'import (je ne sais pas pourquoi....problème avec int64)
    
df[col_tmp]=df[col_tmp].applymap(extr_duration)
df.dtypes

# transformation en float sinon problème à l'import (je ne sais pas pourquoi....problème avec int64)
df["Refparcours"]=df["Refparcours"].map(lambda x: float(x))
df.dtypes

# 2.2. Chargement base de données

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
query = "SELECT * FROM biketours_perfo"
df_DB = pd.read_sql_query(query, conn)
conn.close()

col_acc=df.columns.tolist()

# =============================================================================
# ['Refparcours',
#  'Date',
#  'Distance',
#  'Temps',
#  'Remarques',
#  'Temps_meilleur_catégorie',
#  'Participants_catégorie',
#  'Rang_catégorie',
#  'Temps_meilleur_général',
#  'Participants_général',
#  'Rang_général',
#  'Dénivelé',
#  'Watts_moyens',
#  'Watts_max',
#  'Pente_moyen_montée',
#  'Pente_max_montée',
#  'Pente_moyen_descente',
#  'Pente_max_descente',
#  'Vitesse_max',
#  'Vitesse_montée_moyenne',
#  'Temps_partiel_1',
#  'Temps_partiel_2',
#  'Temps_partiel_3',
#  'Temps_partiel_4',
#  'Temps_partiel_5',
#  'Temps_partiel_6',
#  'Temps_partiel_7',
#  'Temps_partiel_8']
# =============================================================================

col_DB=df_DB.columns.tolist()

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

def create_perf(conn, perf):
    # NB : FC_moy et FC_max n'ont jamais été renseignés !
    sql = ''' INSERT INTO biketours_perfo(Date,
                                          Distance,
                                          Temps,
                                          Remarques,
                                          Dénivelé,
                                          Vitesse_max,
                                          Temps_part_1,
                                          Temps_part_2,
                                          Temps_part_3,
                                          Temps_part_4,
                                          Temps_part_5,
                                          Temps_part_6,
                                          Temps_part_7,
                                          Temps_part_8,
                                          Refparcours_id
                                          )'''+" VALUES"+"("+"?,"*14+"?"+")"
    cur = conn.cursor()
    cur.execute(sql, perf)
        #tour doi être un tuple avec 15 variables !

# ordre lst_col doit correspondre à celui donnée dans create_perf
lst_col=["Date",
         "Distance",
         "Temps",
         "Remarques",
         "Dénivelé",
         "Vitesse_max",
         "Temps_partiel_1",
         "Temps_partiel_2",
         "Temps_partiel_3",
         "Temps_partiel_4",
         "Temps_partiel_5",
         "Temps_partiel_6",
         "Temps_partiel_7",
         "Temps_partiel_8",
         "Refparcours"]


conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")

for i in df[lst_col].itertuples(index=False):
    print(i)
    create_perf(conn, i)
    conn.commit()

conn.close()

####### 3. Importations GARMIN - VERIFIER LES DATES

import pandas as pd
import sqlite3
import datetime
import re
import numpy as np

df = pd.read_csv("C:/Users/chris/Documents/Activities_13012020.csv", header=0, sep=",")
df.columns=df.columns.str.replace(" ","_") # suppression espaces !
df.columns
df.dtypes

df["Gain_alt"]=df["Gain_alt"].str.replace(",","")

# Transformation champ Date
df["Date"]=pd.to_datetime(df["Date"], yearfirst=True) 
df=df.sort_values(by=["Date"], ascending=True)
df["Date"]=df["Date"].map(lambda x: x.date()) 
df.dtypes

## Traitement si colonne manquante
#col_mis=["Fréquence_cardiaque_moyenne", "Fréquence_cardiaque_maximale", "Distance"]
#for c in col_mis:
#    if c not in df.columns:
#       df[c]=None

# Transformation champs FC
df[["Fréquence_cardiaque_moyenne",
      "Fréquence_cardiaque_maximale"]]=df[["Fréquence_cardiaque_moyenne",
      "Fréquence_cardiaque_maximale"]].astype(dtype=np.float64) 

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
df.loc[(df["Type_d'activité"].str.upper() == "INDOOR_CYCLING") & (df["Titre"].str.upper() == "SPINNING"),"Refparcours_id"]=tours_DB.loc[(tours_DB["Parcours"].str.upper() == "SPINNING") ,"id"].iloc[0] 
df.loc[(df["Type_d'activité"].str.upper() == "INDOOR_CYCLING") & (df["Titre"].str.upper() != "SPINNING"),"Refparcours_id"]=tours_DB.loc[(tours_DB["Parcours"].str.upper() == "HOMETRAINER") ,"id"].iloc[0] 
df.loc[(df["Type_d'activité"].str.upper().str.match(r".+_RUNNING$")) ,"Refparcours_id"]=tours_DB.loc[(tours_DB["Type"] == "cap" ) ,"id"].iloc[0] 

df["Refparcours_id"].value_counts(dropna=False)

# ------------ cas VTT et ROUTE : attribution directe si 1 seule variante
uniques=tours_DB.groupby(["Parcours"])["Variante"].count()
uniques=uniques[uniques<=1]
    
catGAR=["mountain_biking","road_biking"]
typeDB=["vtt","route"]
lst=zip(catGAR, typeDB)

for gar, db in lst:
    ref=tours_DB.loc[(tours_DB["Type"]==db) & (tours_DB["Parcours"].isin(uniques.index.tolist())) , :]
    default=tours_DB.loc[tours_DB["Parcours"].str.match(db+"_?"),"id"]
    print(default)
    for t in ref.itertuples(index=False):
#        print(t)
#        print(t.Parcours)
        df.loc[(df["Type_d'activité"]==gar) & (df["Titre"]==t.Parcours), "Refparcours_id"]=t.id
    df.loc[(df["Type_d'activité"]==gar) & (pd.isnull(df["Refparcours_id"])), "Refparcours_id"]=default.iloc[0] 
    #pas ok car default = Series => extraire chiffre
        
df["Refparcours_id"].value_counts(dropna=False)

# Chargement

col_acc=df.columns.tolist()

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

col_DB=df_DB.columns.tolist()

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

####### Tests pour améliorer affectation A INTEGRER : SI 1 SEULE VARIANTE, SI PLUSIEURS TERMES......

conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
query = "SELECT b.id, b.Parcours, b.Variante, c.Type FROM biketours_BikeTour b LEFT JOIN biketours_type c on b.type_id = c.id"
tours_DB = pd.read_sql_query(query, conn)
conn.close()

df = pd.read_csv("C:/Users/chris/Documents/Activities.csv", header=0, sep=",")
df.columns=df.columns.str.replace(" ","_") # suppression espaces !
df.columns
df.dtypes

uniques=tours_DB.groupby(["Parcours"])["Variante"].count()
uniques=uniques[uniques<=1]
    
catGAR=["mountain_biking","road_biking"]
typeDB=["vtt","route"]
lst=zip(catGAR, typeDB)

for gar, db in lst:
    ref=tours_DB.loc[(tours_DB["Type"]==db) & (tours_DB["Parcours"].isin(uniques.index.tolist())) , :]
    default=tours_DB.loc[tours_DB["Parcours"].str.match(db+"_?"),"id"]
    print(default)
    for t in ref.itertuples(index=False):
#        print(t)
#        print(t.Parcours)
        df.loc[(df["Type_d'activité"]==gar) & (df["Titre"]==t.Parcours), "Refparcours_id"]=t.id
    df.loc[(df["Type_d'activité"]==gar) & (pd.isnull(df["Refparcours_id"])), "Refparcours_id"]=default.iloc[0] 
    #pas ok car default = Series => extraire chiffre
        
df["Refparcours_id"].value_counts(dropna=False)





ref=tours_DB["Parcours"]
s="Concise"
s in ref

a=[1,2]
b=2
b in a


df = pd.read_csv("C:/Users/chris/Documents/Activities.csv", header=0, sep=",")
df.columns=df.columns.str.replace(" ","_") # suppression espaces !
df.columns
df.dtypes
a


