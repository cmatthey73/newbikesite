# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 17:19:57 2019

@author: chris
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:33:39 2019

@author: chris
"""

def prepa_data():
    import pandas as pd
    import sqlite3
    import datetime
    
    # Importation données
    conn = sqlite3.connect("C:/Users/chris/newbikesite/db.sqlite3")
    query = '''SELECT a.*, d.*
               FROM biketours_perfo a
               LEFT JOIN 
               ( select b.*, c.Type 
                 FROM biketours_biketour b
                 LEFT JOIN biketours_type c
                 on b.Type_id=c.id) d 
               on a.Refparcours_id = d.id'''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Tranformations
    df["Date"]=pd.to_datetime(df["Date"], dayfirst = True) 
    df["Year"]=df["Date"].dt.year 
  
    return(df)

def trans(v):
    s = v/1000000
    hours = s // 3600
    minutes = (s % 3600) // 60
    seconds = s % 60
    return(str(int(hours))+ ":" + str(int(minutes)).zfill(2) + ":" + str(int(seconds))).zfill(2)


## Graphique évolution date courante
    
def gr_courant(df):
    import seaborn as sns
    import datetime
    
    dt=datetime.date.today()
    df_c=df[(df["Date"].dt.month<dt.month)|((df["Date"].dt.day<=dt.day) & (df["Date"].dt.month==dt.month))]
    df_c_gr=df_c[["Year","Type","Distance", "Temps", "Dénivelé"]].groupby(["Year","Type"],as_index=False).sum()
    df_c_gr["Temps_adapt"]=(df_c_gr["Temps"]/1000000)/3600
    comp_date=sns.catplot(x="Year", y="Temps_adapt", data=df_c_gr.loc[df_c_gr["Year"]>=2008,:], col='Type', kind="bar", col_wrap=2)
    comp_date.savefig("C:/Users/chris/newbikesite/biketours/static/biketours/images/comp_date.png")
    return(comp_date)
