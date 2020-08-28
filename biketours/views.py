from django.shortcuts import render
#from django.http import HttpResponse
import datetime, re
from .models import BikeTour, Perfo, Type
from .forms import AdaptForm
from django.db.models import Sum, Avg, Max, Min, Count, Q
import json

from . import importDB

#from matplotlib import pylab
#from pylab import *
#import PIL, PIL.Image, StringIO

##### Fonctions

def fmt_dct(k, v):  # formatage des résultats agrégés (Nb, Distance_totale/moy, Temps_total/moy, Dénivelé_total/moy)
    if v is None:
        return(v)
    elif re.search("Nb", k) and v is not None:
        return(round(v,0))
    elif re.search("Moy", k) and v is not None:
        return(round(v,1))
    elif (re.search("Distance",k) or re.search("Dénivelé", k)) and v is not None:
        return(format(round(v,2), ","))
    elif re.search("Temps",k) and v is not None:
        s = v.total_seconds()
        hours = s // 3600
        minutes = (s % 3600) // 60
        seconds = s % 60
        return(str(int(hours))+ ":" + str(int(minutes)).zfill(2) + ":" + str(int(seconds))).zfill(2)

def v_moy(qset, suffix): # suffix à introduire manuellement (string)
    if (qset["Distance"+suffix] is None or qset["Temps"+suffix] is None) :
        vmoy=None
    else :
        vmoy=qset["Distance"+suffix]/qset["Temps"+suffix].total_seconds()*3600
    return(vmoy)

def agrperfo(qset, stat="sum", div=3, form=True): # calcul des résultats agrégés (perfo) + mise en forme (! agrégation sur tout le queryset !)
    # calcul des résultats agrégés => res
    if stat=="sum":
        res=qset.aggregate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
        res["Moyenne"]=v_moy(res, "_tot")
    if stat=="avg":
        res=qset.aggregate(Nb=Count("Distance"), Distance_moy=Avg("Distance"), Temps_moy=Avg("Temps"), Dénivelé_moy=Avg("Dénivelé"))
        res["Moyenne"]=v_moy(res, "_moy")
    if stat=="avg_sub": # calcul de moyennes en spécifiant le diviseur (=> moy = sum / div)
        res=qset.aggregate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
        # res={k:(v/div) for k,v in res.items()}    
        for k, v in res.items(): # calcul moyenne basée sur div + gestion None
            if v is None:
                res[k]=None
            else :
                res[k]=v/div
        res["Moyenne"]=v_moy(res, "_tot")
    # mise en forme si form=True
    if form :
        res_form={k:fmt_dct(k, v) for k , v in res.items() }
    else :
        res_form=res
    return(res_form)
    
def comp_anyday(dt, restr=True): # comparaison à la date dt  
    # dt doit être un datetime object !
    # restr=True si types restreints à vtt et vélo de route
    flt=Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month))

    if restr:
        data_comp=Perfo.objects.filter(flt, Q(Refparcours__Type__in=[1, 2]))
        stat_comp_act=agrperfo(Perfo.objects.filter(flt, Q(Refparcours__Type__in=[1, 2]), Q(Date__year=dt.year)), stat="sum")
        stat_comp_act_last=agrperfo(Perfo.objects.filter(flt, Q(Refparcours__Type__in=[1, 2]), Q(Date__year__gte=(dt.year-3)), Q(Date__year__lt=dt.year)), stat="avg_sub",  div=3)
    else:
        data_comp=Perfo.objects.filter(flt)
        stat_comp_act=agrperfo(Perfo.objects.filter(flt, Q(Date__year=dt.year)), stat="sum")
        stat_comp_act_last=agrperfo(Perfo.objects.filter(flt, Q(Date__year__gte=(dt.year-3))&Q(Date__year__lt=dt.year)), stat="avg_sub",  div=3)

    stat_comp = {"dt":dt,
                 "act":stat_comp_act,
                 "last":stat_comp_act_last,
                 "data":data_comp}
    return(stat_comp)
    
def comp_today(restr=True): # comparaison à la date actuelle  
    dt=datetime.date.today()
    stat_comp=comp_anyday(dt=dt, restr=restr)
    return(stat_comp)

#def comp_anyOLD(qset, y=None, restr=True): # autres comparaisons, comp gérée lors de la création de qset ! 
#    if y is None:
#        dt=datetime.date.today()
#    else:
#        dt=datetime.date(int(y),1,1)
#    data_comp = qset
#    if restr:
#        tours = BikeTour.objects.filter(Type__in=[1, 2]).values_list('id', flat=True)
#    else:
#        tours = BikeTour.objects.values_list('id', flat=True)
#    stat_comp_act=agrperfo(data_comp.filter(Q(Date__year=dt.year)&Q(Refparcours__in = tours)), stat="sum")
#    stat_comp_act_last=agrperfo(data_comp.filter(Q(Date__year__gte=(dt.year-3))&Q(Date__year__lt=dt.year)&Q(Refparcours__in = tours)), stat="avg_sub",  div=3)
#    stat_comp = {"dt":dt,
#                 "act":stat_comp_act,
#                 "last":stat_comp_act_last,
#                 "data":data_comp}
#    return(stat_comp)
    
def comp_any(filt=Q(Date__month__lt=99), y=None, restr=True): 
    # autres comparaisons basées sur perfo, filtre initial (appliqué à Perfo) à renseigner !
    # filtre par défaut = filtre inutile => = pas de filtre !
    if y is None:
        dt=datetime.date.today()
    else:
        dt=datetime.date(int(y),1,1)

    if restr: 
        data=Perfo.objects.filter(filt, Q(Refparcours__Type__in=[1, 2]))
        stat_comp_act=agrperfo(Perfo.objects.filter(filt, Q(Date__year=dt.year), Q(Refparcours__Type__in=[1, 2])), stat="sum")
        stat_comp_act_last=agrperfo(Perfo.objects.filter(filt, Q(Date__year__gte=(dt.year-3)), Q(Date__year__lt=dt.year), Q(Refparcours__Type__in=[1, 2])), stat="avg_sub",  div=3)
    else:
        data=Perfo.objects.filter(filt)
        stat_comp_act=agrperfo(Perfo.objects.filter(filt, Q(Date__year=dt.year)), stat="sum")
        stat_comp_act_last=agrperfo(Perfo.objects.filter(filt, Q(Date__year__gte=(dt.year-3)), Q(Date__year__lt=dt.year)), stat="avg_sub",  div=3)

    stat_comp = {"dt":dt,
                 "act":stat_comp_act,
                 "last":stat_comp_act_last,
                 "data":data}
    return(stat_comp)
        
def prep_JSON(flt, ylim=2008): 

    data_dist=list()
    data_t=list()
    data_deniv=list()
    data_n=list()
    
    if flt is None :
                lst_y=[y.year for y in Perfo.objects.all().dates("Date", "year", order="ASC") if y.year>=ylim]
    else :
                lst_y=[y.year for y in Perfo.objects.filter(flt).dates("Date", "year", order="ASC") if y.year>=ylim]
        
    for y in lst_y:
        tmp=list()
        for t in Type.objects.values_list("Type", flat=True):
            if flt is None :
                tmp.append(agrperfo(Perfo.objects.filter(Q(Date__year=y), Q(Refparcours__Type__Type=t)), form=False))
            else :
                tmp.append(agrperfo(Perfo.objects.filter(flt, Q(Date__year=y), Q(Refparcours__Type__Type=t)), form=False))
        data_dist.append({"name":y, "data":[0 if k["Distance_tot"] is None else k["Distance_tot"] for k in tmp] })
        data_t.append({"name":y, "data":[0 if k["Temps_tot"] is None else round(k["Temps_tot"].total_seconds()/3600,1) for k in tmp]})
        data_deniv.append({"name":y, "data":[0 if k["Dénivelé_tot"] is None else k["Dénivelé_tot"] for k in tmp]})
        data_n.append({"name":y, "data":[0 if k["Nb"] is None else k["Nb"] for k in tmp] })
                    
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Distance par activité'},
#        'xAxis': {'categories': type_bike},
        'xAxis': {'categories': list(Type.objects.values_list("Type", flat=True))},
        'yAxis': {
                  'title': {
                              'enabled': True,
                              'text': 'Distance (km)',
                              'style': {
                                      'fontWeight': 'normal',
#                                      'color':'black'
                                      }
                             }
                    },
        'series': data_dist
    }
                              
    dist = json.dumps(chart)
     
    chart.update({'title': {'text': 'Temps par activité'},
                  'yAxis': {'dateTimeLabelFormats' : {
                                                        'hour': '%H:%M',
                                                     },         
                            'title': {
                                       'text': 'Temps (heures)'
                                       }},
                  'series':data_t})
                              
    time = json.dumps(chart)

    chart.update({'title': {'text': 'Dénivelé par activité'},
                  'yAxis': {'title': {
                                       'text': 'Dénivelé (m)'
                                       }},
                  'series':data_deniv})
                              
    deniv = json.dumps(chart)

    context = {"dist":dist,
               "time":time,
               "deniv":deniv}
    
    return context

def prep_JSON_start(): 

    dt=datetime.date.today()
    flt=(Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month)))

#    data_dist=list()
    data_t=list()
#    data_deniv=list()
#    data_n=list()
#    data_dist_l3=list()
    data_t_l3=list()
#    data_deniv_l3=list()
#    data_n_l3=list()
    
    for t in Type.objects.values_list("Type", flat=True):
        tmp=list()
        tmp_l3=list()
        lst_m={y.month for y in Perfo.objects.filter(flt).dates("Date", "month", order="ASC")}
        for y in lst_m:
            tmp.append(agrperfo(Perfo.objects.filter(flt, Q(Date__month__lte=y), Q(Date__year=dt.year), Q(Refparcours__Type__Type=t)), form=False))
            tmp_l3.append(agrperfo(Perfo.objects.filter(flt, Q(Date__month__lte=y), Q(Date__year__gte=(dt.year-3)), Q(Date__year__lt=dt.year), Q(Refparcours__Type__Type=t)), stat="avg_sub",  div=3, form=False))
        
        # ---- séries année courante
#        data_dist.append({"name":t, "data":[0 if k["Distance_tot"] is None else k["Distance_tot"] for k in tmp] })
        data_t.append({"name":t, "data":[0 if k["Temps_tot"] is None else round(k["Temps_tot"].total_seconds()/3600,1) for k in tmp]})
#        data_deniv.append({"name":t, "data":[0 if k["Dénivelé_tot"] is None else k["Dénivelé_tot"] for k in tmp]})
#        data_n.append({"name":t, "data":[0 if k["Nb"] is None else k["Nb"] for k in tmp] })
        
        # ---- séries années last_3
#        data_dist_l3.append({"name":t, "data":[0 if k["Distance_tot"] is None else k["Distance_tot"] for k in tmp_l3] })
        data_t_l3.append({"name":t, "data":[0 if k["Temps_tot"] is None else round(k["Temps_tot"].total_seconds()/3600,1) for k in tmp_l3]})
#        data_deniv_l3.append({"name":t, "data":[0 if k["Dénivelé_tot"] is None else k["Dénivelé_tot"] for k in tmp_l3]})
#        data_n_l3.append({"name":t, "data":[0 if k["Nb"] is None else k["Nb"] for k in tmp_l3] })

#   area chart
    chart={"chart": { "type": 'area'},
           "title": {
                       "text": 'Année courante'
                     },
           "subtitle": {
                           "text": '- Heures cumulées -'
                        },
           "xAxis": {
                       "categories": list(lst_m),
                       "tickmarkPlacement": 'on',
                       "title": {
                               "enabled": False
                               }
                    },
          "yAxis": {
                      "title": {
                              "text": 'Hrs'
                              }
                     ,"max":150
                   },
         "tooltip": {
                     "split": True,
                     "valueSuffix": " hrs"
                    },
        "plotOptions": {
                        "area": {
                                 "stacking": "normal",
                                 "lineColor": "#666666",
                                 "lineWidth": 1,
                                 "marker": {
                                             "lineWidth": 1,
                                             "lineColor": '#666666'
                                            }
                                 }
                      },
        "series": data_t
        }

    chart_t = json.dumps(chart)
    
    chart.update({"title": {"text": 'Moyenne 3 dernières années'},
                  "series":data_t_l3})
                                 
    chart_t_l3=json.dumps(chart)
    
    context = {"chart_t":chart_t,
               "chart_t_l3":chart_t_l3}
    
    return context
  

##### Listes de choix

def index(request):
    lst_link = {"Tours":"biketours/tours", "Statistiques":"biketours/stat", "Graphiques":"biketours/graph", 
                "Listes":"biketours/list", 
                "Introduction données":"biketours/input", "Tests":"biketours/tests"}
    stat_comp = comp_today()
    stat_comp_all = comp_today(restr=False)
    context = {"lst_link":lst_link,
               "dt":stat_comp["dt"],
               "stat_comp_act":stat_comp["act"],
               "stat_comp_act_last":stat_comp["last"],
               "stat_comp_all_act":stat_comp_all["act"],
               "stat_comp_all_act_last":stat_comp_all["last"]}
    context.update({"chart_tot":prep_JSON_start()})
    return render(request, "biketours/main_index.html", context)

def index_tours(request):
    all_tours = BikeTour.objects.all().order_by("Parcours", "Variante")
    context = {"all_tours":all_tours}
    return render(request, "biketours/tours.html" ,context)

def index_stat(request):
    lst_link = {"Comparaison":"biketours/stat/comp", "Par mois":"biketours/stat/month", "Par année":"biketours/stat/year", "Par activité":"biketours/stat/act"}
    context = {"lst_link":lst_link}
    return render(request, "biketours/main_index.html", context)

def index_graph(request):
    lst_link = {"Comparaison":"biketours/graph/comp", "Totaux annuels":"biketours/graph/year", "Mois courant":"biketours/graph/month"}
    context = {"lst_link":lst_link}
    return render(request, "biketours/main_index.html", context)

def index_list(request):
    lst_link = {"Par mois":"biketours/list/month", "Par activité":"biketours/list/act"}
    context = {"lst_link":lst_link}
    return render(request, "biketours/main_index.html", context)

##### 1. Détails perfos

def perf_tours(request, tour_id): 
    all_perf = Perfo.objects.filter(Refparcours=tour_id).order_by("-Date")
    tour = BikeTour.objects.get(pk=tour_id)
    
    # Valeurs moyennes par année
    perf_y=dict()
    for y in all_perf.dates("Date", "year", order="DESC") :
        perf_y[y.year] = agrperfo(all_perf.filter(Date__year=y.year), stat="avg")
        
    context = {"all_perf":all_perf,
               "perf_y":perf_y,
               "tour":tour}
    return render(request, "biketours/perfo.html" ,context)

def det_perf(request, perf_id): 
    perf = Perfo.objects.get(pk=perf_id)
    perf_old = agrperfo(Perfo.objects.filter(Refparcours=perf.Refparcours), stat="avg")
    if request.method == "POST": # au moment du renvoi du formulaire
        form = AdaptForm(request.POST, instance=perf)# instance = ... permet de mettre à jour une données existante !
        if form.is_valid(): 
            form.save()
    else: # au moment du 1er appel de la view
        form = AdaptForm(instance=perf)
               # initial = ... permet de de donner des valeurs initiales (ici celles de perf) !
            
    context = {"perf":perf,
               "perf_old":perf_old,
               "form":form}
    return render(request, "biketours/det_perf.html" ,context)

##### 2. Statistiques
    
## Stats comparaison jour 
    
def stat_comp(request):

    if request.method == "POST": # au moment du renvoi du formulaire
        dt = request.POST["alt_date"]
        dt = datetime.datetime.strptime(dt, "%Y-%m-%d")
        # valeurs totales : année en cours + moyenne 3 dernières années
        stat_comp = comp_anyday(dt)
        stat_comp_all = comp_anyday(dt, restr=False)
    else: # au moment du 1er appel de la view
        # valeurs totales : année en cours + moyenne 3 dernières années
        stat_comp = comp_today()
        stat_comp_all = comp_today(restr=False)
        dt=stat_comp["dt"]
        
    # valeurs par activité, par année
    stat_comp_act_y = dict()
    for t in Type.objects.values_list("pk", flat=True) :
        tours = BikeTour.objects.filter(Type=t).values_list('id', flat=True).order_by('id')
        data_comp_y = stat_comp_all["data"].filter(Refparcours__in = tours)
        tmp=dict()
        for y in Perfo.objects.dates("Date", "year", order="DESC") :
                data_comp_act_y = data_comp_y.filter(Date__year=y.year)
                tmp[y.year]= agrperfo(data_comp_act_y, stat="sum")
                stat_comp_act_y[Type.objects.get(pk=t).Type] = tmp
        
    context = {
               "dt":dt,
               "stat_comp_act":stat_comp["act"],
               "stat_comp_act_last":stat_comp["last"],
               "stat_comp_all_act":stat_comp_all["act"],
               "stat_comp_all_act_last":stat_comp_all["last"],
               "stat_comp_act_y":stat_comp_act_y
               }
    return render(request, "biketours/stat_comp.html", context)

## Stats mensuelles 

def month(request):
    mth = Perfo.objects.dates("Date", "month", order="ASC")
    lst_mth=[]
    for i in mth :
        if i.month not in lst_mth :
            lst_mth.append(i.month)
    lst_mth.sort()
    context = {"lst_mth":lst_mth}
    return render(request, "biketours/stat_month_index.html", context)

def stat_month(request, mth_id): 
    data_y = Perfo.objects.filter(Date__month=mth_id)
    
    # valeurs totales : mois en cours + moyenne 3 dernières années
    stat_comp=comp_any(filt=Q(Date__month=mth_id))
    stat_comp_all=comp_any(filt=Q(Date__month=mth_id), restr=False)
        
    # valeurs mensuelles par activité, par année       
    stat_comp_act_y = dict()
    for t in Type.objects.values_list("pk", flat=True) :
        tours = BikeTour.objects.filter(Type=t).values_list('id', flat=True).order_by('id')
        data_comp_y = data_y.filter(Refparcours__in = tours)
        tmp=dict()
        for y in Perfo.objects.dates("Date", "year", order="DESC") :
            data_comp_act_y = data_comp_y.filter(Date__year=y.year)
            tmp[y.year]= agrperfo(data_comp_act_y, stat="sum")
        stat_comp_act_y[Type.objects.get(pk=t).Type] = tmp
    
    context={
             "stat_comp_act":stat_comp["act"],
             "stat_comp_act_last":stat_comp["last"],
             "stat_comp_all_act":stat_comp_all["act"],
             "stat_comp_all_act_last":stat_comp_all["last"],
             "stat_comp_act_y":stat_comp_act_y,
             "mth_id":mth_id}
    return render(request, "biketours/stat_month.html", context)

## Stats annuelles

def years(request):
    lst_yr = Perfo.objects.dates("Date", "year", order="DESC")
    context = {"lst_yr":lst_yr}
    return render(request, "biketours/stat_year_index.html", context)

def stat_year(request, year_id):
    
    # valeurs totales : année en cours + moyenne 3 dernières années
    stat_comp=comp_any(y=year_id)
    stat_comp_all=comp_any(y=year_id, restr=False)
        
    # valeurs annuelles
    data_y = Perfo.objects.filter(Date__year=year_id)
    stat_y = agrperfo(data_y, stat="sum")
    
    # valeurs annuelles par activité
    stat_y_act = dict()
    for t in Type.objects.values_list("pk", flat=True) :
        l_t = BikeTour.objects.filter(Type=t).values_list("pk", flat=True)
        tp = Type.objects.get(pk=t).Type
        stat_y_act[tp] = agrperfo(data_y.filter(Refparcours__in = l_t), stat="sum")
    
    context={
             "stat_comp_act":stat_comp["act"],
             "stat_comp_act_last":stat_comp["last"],
             "stat_comp_all_act":stat_comp_all["act"],
             "stat_comp_all_act_last":stat_comp_all["last"],
             "stat_y":stat_y,
             "stat_y_act":stat_y_act,
             "year_id":year_id}
    return render(request, "biketours/stat_year.html", context)

## Stats par activité
    
def activ(request):
    lst_act = Type.objects.all()
    context = {"lst_act":lst_act}
    return render(request, "biketours/stat_act_index.html", context)

def stat_act(request, act_id):
    # valeurs par activité
    stat_comp=comp_any(Q(Refparcours__Type=act_id), restr=False)
       
    # valeurs par activité, par année
    stat_act_y = dict()
    for y in Perfo.objects.dates("Date", "year", order="DESC") :
        data_act_y = Perfo.objects.filter(Refparcours__Type=act_id, Date__year=y.year)
        stat_act_y[y.year] = agrperfo(data_act_y, stat="sum")
    
    context = {
               "stat_comp_act":stat_comp["act"],
               "stat_comp_act_last":stat_comp["last"],
               "stat_act_y":stat_act_y,
               "act":Type.objects.get(pk=act_id)}
    return render(request, "biketours/stat_act.html", context)

#### 3. Graph A DEVELOPPER !!!

def graph_year(request):
    flt=None
    context = prep_JSON(flt)
    context.update({"t":"Valeurs annuelles"})
    return render(request, "biketours/graph.html" ,context)

def graph_month(request):
    dt=datetime.date.today()
    flt=Q(Date__month=dt.month)
    context = prep_JSON(flt)
    context.update({"t":"Valeurs mois courant : "+str(dt.strftime("%B"))})
    return render(request, "biketours/graph.html" ,context)

def graph_comp(request):
    dt=datetime.date.today()
    flt=Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month))
    context = prep_JSON(flt)
    context.update({"t":"Valeurs au "+str(dt)})
    return render(request, "biketours/graph.html" ,context)

##### 4. Listes

def list_m(request, mth_id):
    list_m = Perfo.objects.filter(Date__month=mth_id)
    list_m_y = dict()
    for y in Perfo.objects.dates("Date", "year", order="DESC") :
        list_m_y[y.year] = list_m.filter(Date__year=y.year).order_by("Date")
    context = {"list":list_m_y,
				"type":"mois",
				"det":mth_id}
    return render(request, "biketours/list.html" ,context)

def list_act(request, act_id):
    list_a = Perfo.objects.filter(Refparcours__Type=act_id)
    list_a_y = dict()
    for y in Perfo.objects.dates("Date", "year", order="DESC") :
        list_a_y[y.year] = list_a.filter(Date__year=y.year).order_by("Date")
    context = {"list":list_a_y,
				"type":"activité",
				"det":Type.objects.get(pk=act_id).Type}
    return render(request, "biketours/list.html" ,context)    
    
##### 5. Input données

def datainput(request):
    data = {}
    if "GET" == request.method:
        return render(request, "biketours/input.html", data)
        # if not GET, then proceed
    else:
        csv_file = request.FILES["csv_file"]  
        test = csv_file.name
        if not csv_file.name.endswith('.csv'):
            return render(request, "biketours/input.html", data)
        else:
            importDB.import_garmin(test)
            context = {"test":test}
            return render(request, "biketours/input.html" ,context)

##### 9999. Tests

def tests(request):
    ylim=2008
    dt=datetime.date.today()
    flt=Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month))
    qset=Perfo.objects.filter(flt)
    sel=True
    
    type_bike=list()
    ser_dist=list()
    ser_time=list()
    ser_deniv=list()
    
    # test1 = json - graphiqe
    if sel:
        tours=BikeTour.objects.filter(Type__in=[1, 2]).values_list('id', flat=True)
        qset=qset.filter(Refparcours__in = tours)
  
    lst_act=BikeTour.objects.filter(id__in = qset.values_list("Refparcours", flat=True)).values_list("Type", flat=True)
    lst_act_unique=set(lst_act)
    
    for y in qset.filter(Date__year__gte=ylim).dates("Date", "year", order="ASC") :
        data_y = qset.filter(Date__year=y.year)
        tmp=dict()
        dist_bike=list()
        time_bike=list()
        deniv_bike=list()
        for t in lst_act_unique :
            l_t = BikeTour.objects.filter(Type=t).values_list("pk", flat=True)
            tp = Type.objects.get(pk=t).Type
            tmp[tp] = data_y.filter(Refparcours__in = l_t).aggregate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
            if tp not in type_bike:
                    type_bike.append(tp)
            if not tmp[tp]["Distance_tot"] is None:
                dist_bike.append(round(tmp[tp]["Distance_tot"],0))
            else:
                dist_bike.append(0)
            if not tmp[tp]["Temps_tot"] is None:
                time_bike.append(round(tmp[tp]["Temps_tot"].total_seconds()/3600,1))
            else :
                time_bike.append(0)
            deniv_bike.append(tmp[tp]["Dénivelé_tot"])
    
        serie = {'name': y.year,
                 'data': dist_bike,
#                 'color': 'blue',
#                 'dataLabels': {
#                         'enabled': True}
                 }
        ser_dist.append(serie)
        
        serie = {'name': y.year,
                 'data': time_bike,
#                 'color': 'red'
                 }
        ser_time.append(serie)
#        
        serie = {'name': y.year,
                 'data': deniv_bike,
#                 'color': 'green'
                }
        ser_deniv.append(serie)
                    
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Distance par activité'},
        'xAxis': {'categories': type_bike},
        'yAxis': {
                  'title': {
                              'enabled': True,
                              'text': 'Distance (km)',
                              'style': {
                                      'fontWeight': 'normal',
#                                      'color':'black'
                                      }
                             }
                    },
        'series': ser_dist
    }
                              
    dist = json.dumps(chart)
     
    chart.update({'title': {'text': 'Temps par activité'},
                  'yAxis': {'dateTimeLabelFormats' : {
                                                        'hour': '%H:%M',
                                                     },         
                            'title': {
                                       'text': 'Temps (heures)'
                                       }},
                  'series':ser_time})
    time = json.dumps(chart)

    chart.update({'title': {'text': 'Dénivelé par activité'},
                  'yAxis': {'title': {
                                       'text': 'Dénivelé (m)'
                                       }},
                  'series':ser_deniv})
    deniv = json.dumps(chart)
    
    ######### ESSAI SUR LIENS ENTRE TABLES ####################
    # lien forward, p.ex. perfo => biketour, foreignkey__champ
    # lien backward, p.ex. biketour => perfo, nom_model__champ
    
    # problématique des filters enchaînés : https://stackoverflow.com/questions/8164675/chaining-multiple-filter-in-django-is-this-a-bug
    # complex lookups : https://docs.djangoproject.com/en/dev/topics/db/queries/#complex-lookups-with-q-objects
    
    # test2 = aggregate django-style (backward relation)
    agr = BikeTour.objects.annotate(Nb=Count("perfo__Distance"), Distance_tot=Sum("perfo__Distance"), Temps_tot=Sum("perfo__Temps"), Dénivelé_tot=Sum("perfo__Dénivelé"))
    agr2 = Type.objects.annotate(Nb=Count("biketour__perfo__Distance"), Distance_tot=Sum("biketour__perfo__Distance"), Temps_tot=Sum("biketour__perfo__Temps"), Dénivelé_tot=Sum("biketour__perfo__Dénivelé"))
        
    # test3 = remonter champs (forward relation)
    tp=Perfo.objects.filter(Date__year=2020).values("Date","Refparcours__Parcours", "Refparcours__Type__Type")
    tp2=Perfo.objects.filter(Date__year=2020)
    tp3=[(v.Refparcours.Parcours, v.Refparcours.Type, v.Refparcours.But) for v in Perfo.objects.filter(Date__year=2020)]
   
    # essai agrégation par activité, marche !
    flt=Q(biketour__Type__in=[1, 2])&Q(biketour__perfo__Date__year=2019)
    test3=Type.objects.filter(flt).annotate(Nb=Count("biketour__perfo__Distance"), Distance_tot=Sum("biketour__perfo__Distance"), Temps_tot=Sum("biketour__perfo__Temps"), Dénivelé_tot=Sum("biketour__perfo__Dénivelé"))
    test4={k.Type:{"Nb":k.Nb, "Distance_tot":k.Distance_tot, "Temps_tot":k.Temps_tot, "Dénivelé_tot":k.Dénivelé_tot} for k in test3}
    test4_form={k:{i:fmt_dct(i, j) for i, j in v.items()} for k, v in test4.items() }
    
    # essai agrégation par année avec sélection vtt/route, marche !
    flt=Q(Refparcours__Type__in=[1, 2])
    test5=Perfo.objects.filter(flt).dates("Date", "year", order="DESC").values("datefield").annotate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
    test5b={k["datefield"]:{"Nb":k["Nb"], "Distance_tot":k["Distance_tot"], "Temps_tot":k["Temps_tot"], "Dénivelé_tot":k["Dénivelé_tot"]} for k in test5}
    test5_form={k:{i:fmt_dct(i, j) for i, j in v.items()} for k, v in test5b.items() }

    # essai agrégation après multiples filter
    flt1=Q(Refparcours__Type__in=[1, 2,3])
    flt2=Q(Date__year__gte=2016)
    flt3=Q(Date__month=4)
    flt4=Q(Dénivelé__gt=500)
    test6=Perfo.objects.filter(flt1, flt2, flt3, flt4).dates("Date", "year", order="DESC").values("datefield").annotate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
    test6b={k["datefield"]:{"Nb":k["Nb"], "Distance_tot":k["Distance_tot"], "Temps_tot":k["Temps_tot"], "Dénivelé_tot":k["Dénivelé_tot"]} for k in test6}
    test6_form={k:{i:fmt_dct(i, j) for i, j in v.items()} for k, v in test6b.items() }

    ######### ESSAI POUR NOUVEAUX GRAPHIQUES ####################
    
    ylim=2008
    dt=datetime.date.today()
    flt=(Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month)))
    test7=Perfo.objects.filter(flt, Q(Date__year=dt.year)).dates("Date", "month", order="ASC").values("datefield").annotate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
    
    data_dist=list()
    data_t=list()
    data_deniv=list()
    data_n=list()
    data_dist_l3=list()
    data_t_l3=list()
    data_deniv_l3=list()
    data_n_l3=list()
    
    for t in Type.objects.values_list("Type", flat=True):
        tmp=list()
        tmp_l3=list()
        lst_m={y.month for y in Perfo.objects.filter(flt).dates("Date", "month", order="ASC")}
        for y in lst_m:
            tmp.append(agrperfo(Perfo.objects.filter(flt, Q(Date__month__lte=y), Q(Date__year=dt.year), Q(Refparcours__Type__Type=t)), form=False))
            tmp_l3.append(agrperfo(Perfo.objects.filter(flt, Q(Date__month__lte=y), Q(Date__year__gte=(dt.year-3)), Q(Date__year__lt=dt.year), Q(Refparcours__Type__Type=t)), stat="avg_sub",  div=3, form=False))
        # séries année courante
        data_dist.append({"name":t, "data":[0 if k["Distance_tot"] is None else k["Distance_tot"] for k in tmp] })
        data_t.append({"name":t, "data":[0 if k["Temps_tot"] is None else round(k["Temps_tot"].total_seconds()/3600,1) for k in tmp]})
        data_deniv.append({"name":t, "data":[0 if k["Dénivelé_tot"] is None else k["Dénivelé_tot"] for k in tmp]})
        data_n.append({"name":t, "data":[0 if k["Nb"] is None else k["Nb"] for k in tmp] })
        # séries années last_3
        data_dist_l3.append({"name":t, "data":[0 if k["Distance_tot"] is None else k["Distance_tot"] for k in tmp_l3] })
        data_t_l3.append({"name":t, "data":[0 if k["Temps_tot"] is None else round(k["Temps_tot"].total_seconds()/3600,1) for k in tmp_l3]})
        data_deniv_l3.append({"name":t, "data":[0 if k["Dénivelé_tot"] is None else k["Dénivelé_tot"] for k in tmp_l3]})
        data_n_l3.append({"name":t, "data":[0 if k["Nb"] is None else k["Nb"] for k in tmp_l3] })


#   area chart
    chart={"chart": { "type": 'area'},
           "title": {
                       "text": 'Année courante'
                     },
           "subtitle": {
                           "text": '- Heures cumulées -'
                        },
           "xAxis": {
                       "categories": list(lst_m),
                       "tickmarkPlacement": 'on',
                       "title": {
                               "enabled": False
                               }
                    },
          "yAxis": {
                      "title": {
                              "text": 'Hrs'
                              }
#                     ,"max":200
                   },
         "tooltip": {
                     "split": True,
                     "valueSuffix": " hrs"
                    },
        "plotOptions": {
                        "area": {
                                 "stacking": "normal",
                                 "lineColor": "#666666",
                                 "lineWidth": 1,
                                 "marker": {
                                             "lineWidth": 1,
                                             "lineColor": '#666666'
                                            }
                                 }
#                        "area": {
#                                 "pointStart": 1,
#                                 "marker": {
#                                             "enabled": False,
#                                             "symbol": 'circle',
#                                             "radius": 2,
#                                             "states": {
#                                                         "hover": {
#                                                                     "enabled": True
#                                                                     }
#                                                         }
#                                            }
#                                }
                      },
        "series": data_t
#        "series": [{
#                        "name": 'Asia',
#                        "data": [502, 635, 809, 947, 1402, 3634, 5268]
#                    }, {
#                        "name": 'Africa',
#                        "data": [106, 107, 111, 133, 221, 767, 1766]
#                    }, {
#                        "name": 'Europe',
#                        "data": [163, 203, 276, 408, 547, 729, 628]
#        }
#                    ]
        }

    test_chart = json.dumps(chart)
    
    chart.update({"title": {"text": 'Moyenne 3 dernières années'},
                  "series":data_t_l3})
    test_chart_l3=json.dumps(chart)
    
    context = {"dist":dist,
               "time":time,
               "deniv":deniv,
               "agr":agr,
               "agr2":agr2
               ,"type":tp
               ,"type2":tp2
               ,"type3":tp3
               ,"test3":test3
               ,"test4":test4_form
               ,"test5":test5_form
               ,"test6":test6_form
               ,"test7":test7
               ,"test_chart":test_chart
               ,"test_chart_l3":test_chart_l3
               ,"test_n":data_t_l3
                              }

    
    return render(request, "biketours/tests.html" ,context)




###### plus utilisé
    
def prep_JSON_startOLD(ylim=2008, sel=False): 
    # à adapter, 
    # - doit permettre agrégation step1 par année OU activité
    
    dt=datetime.date.today()
    flt=Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month))
    qset=(Perfo.objects.filter(flt))
    
    categ=list()
    ser_dist=list()
    ser_time=list()
    ser_deniv=list()
            
    if sel:
        qset=qset.filter(Refparcours__Type__in=[1, 2]) # ne fonctionne vraisemblablement pas, à tester ---- NB : pas utilisé
  
    lst_act=BikeTour.objects.filter(id__in = qset.values_list("Refparcours", flat=True)).values_list("Type", flat=True)
    lst_act_unique=set(lst_act)
    dt=datetime.date.today()
    
    data={"y":qset.filter(Date__year=dt.year),
          "last_3y":qset.filter(Q(Date__year__gte=(dt.year-3))&Q(Date__year__lt=dt.year))
          }
    
    for t in lst_act_unique :
        dist_bike=list()
        time_bike=list()
        deniv_bike=list()
        l_t = BikeTour.objects.filter(Type=t).values_list("pk", flat=True)
        tp = Type.objects.get(pk=t).Type
        for k, v in data.items():
            if k=="last_3y":
                l=3
            else:
                l=1
            if k not in categ:
                categ.append(k)
            tmp = v.filter(Refparcours__in = l_t).aggregate(Nb=Count("Distance"), Distance_tot=Sum("Distance"), Temps_tot=Sum("Temps"), Dénivelé_tot=Sum("Dénivelé"))
            if not tmp["Distance_tot"] is None:
                 dist_bike.append(round(tmp["Distance_tot"]/l,0))
            else:
                 dist_bike.append(0)
            if not tmp["Temps_tot"] is None:
                 time_bike.append(round(tmp["Temps_tot"].total_seconds()/3600/l,1))
            else :
                 time_bike.append(0)
            if not tmp["Dénivelé_tot"] is None:
                 deniv_bike.append(tmp["Dénivelé_tot"]/l)
            else:
                deniv_bike.append(0)
        
        serie = {'name': tp,
                 'data': dist_bike,
        #                 'color': 'blue',
        #                 'dataLabels': {
        #                         'enabled': True}
                    }
        ser_dist.append(serie)
                
        serie = {'name': tp,
                 'data': time_bike,
        #                 'color': 'red'
                    }
        ser_time.append(serie)
        #        
        serie = {'name': tp,
                 'data': deniv_bike,
        #                 'color': 'green'
                    }
        ser_deniv.append(serie)

    chart = {
        'chart': {'type': 'bar'},
        'title': {'text': 'Temps par activité'},
        'xAxis': {'categories': categ},
        'yAxis': { 'dateTimeLabelFormats' : {
                                                'hour': '%H:%M',
                                                },                               
                  'title': {
                              'enabled': True,
                              'text': 'Temps (heures)',
                              'style': {
                                      'fontWeight': 'normal',
#                                      'color':'black'
                                      }
                             },
                  'max':200
                  },
        'plotOptions': {
                       'bar': {
                                   'stacking': 'normal',
                                    'dataLabels': {
                                                      'enabled': True
                                                      }
                                      }
                        },
        'series': ser_time
    }
      
    time = json.dumps(chart)

    context = {"time":time}
    
    return context
