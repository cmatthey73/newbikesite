# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:33:39 2019

@author: chris
"""

import pandas as pd
import sqlite3
#import matplotlib.pyplot as plt
import seaborn as sns
import datetime

def trans(v):
    s = v/1000000
    hours = s // 3600
    minutes = (s % 3600) // 60
    seconds = s % 60
    return(str(int(hours))+ ":" + str(int(minutes)).zfill(2) + ":" + str(int(seconds))).zfill(2)

### Importation données

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

df["Date"]=pd.to_datetime(df["Date"], dayfirst = True) 

df["Year"]=df["Date"].dt.year 
#df["Temps"]=df["Temps"] *datetime.timedelta(microseconds=1)

## Graphique évolution date courante

dt=datetime.date.today()
df_c=df[(df["Date"].dt.month<dt.month)|((df["Date"].dt.day<=dt.day) & (df["Date"].dt.month==dt.month))]
df_c_gr=df_c[["Year","Type","Distance", "Temps", "Dénivelé"]].groupby(["Year","Type"],as_index=False).sum()
df_c_gr["Temps_adapt"]=(df_c_gr["Temps"]/1000000)/3600
comp_date=sns.catplot(x="Year", y="Temps_adapt", data=df_c_gr.loc[df_c_gr["Year"]>=2008,:], col='Type', kind="bar", col_wrap=2)
comp_date.savefig("C:/Users/chris/newbikesite/biketours/static/biketours/images/comp_date.png")

## Graphique totaux annuels

df_y_gr=df[["Year","Type","Distance", "Temps", "Dénivelé"]].groupby(["Year","Type"],as_index=False).sum()
df_y_gr["Temps_adapt"]=(df_y_gr["Temps"]/1000000)/3600
comp_date=sns.catplot(x="Year", y="Temps_adapt", data=df_y_gr.loc[df_y_gr["Year"]>=2008,:], col='Type', kind="bar", col_wrap=2)
comp_date.savefig("C:/Users/chris/newbikesite/biketours/static/biketours/images/comp_y.png")

## Graphique mois courant

df_m=df[(df["Date"].dt.month==dt.month)]
df_m_gr=df_m[["Year","Type","Distance", "Temps", "Dénivelé"]].groupby(["Year","Type"],as_index=False).sum()
df_m_gr["Temps_adapt"]=(df_m_gr["Temps"]/1000000)/3600
comp_date=sns.catplot(x="Year", y="Temps_adapt", data=df_m_gr.loc[df_c_gr["Year"]>=2008,:], col='Type', kind="bar", col_wrap=2)
comp_date.savefig("C:/Users/chris/newbikesite/biketours/static/biketours/images/comp_m.png")



#### test DEV


test={2006:{"Nb":[50], "Dist":150},
      2007:{"Nb":[150], "Dist":500},
      2008:{"Nb":[180], "Dist":600}
      }
df_test=pd.DataFrame.from_dict(test[2006])

# DataFrame.append(other, ignore_index=False, verify_integrity=False, sort=None)
for k,v in test.items():
    df_test.append(v, ignore_index=True)
    
### graphique matplotlib/seaborn

df["Year"]=pd.to_datetime(df["Date"])
df["Year"]=df["Year"].map(lambda x: x.year)

sns.lmplot("Year", "Distance", data=df, fit_reg=False, col='Type', col_wrap=2)

df_gr=df[["Year","Type","Distance", "Temps", "Dénivelé"]].groupby(['Year','Type'],as_index=False).sum()
pl=df_gr.plot(kind='bar',stacked=True)

sns.set_style("whitegrid")
sns.catplot(x="Year", y="Temps", data=df_gr.loc[df_gr["Year"]>=2008,:], col='Type', kind="bar", col_wrap=2)
test=sns.relplot(x="Year", y="Temps", data=df_gr.loc[df_gr["Year"]>=2008,:], hue='Type', kind="line")
test.savefig("C:/Users/chris/newbikesite/biketours/static/biketours/images/test.png")

df_gr.columns

