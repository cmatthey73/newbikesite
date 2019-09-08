from django.shortcuts import render
from django.http import HttpResponse
import datetime, re
from .models import BikeTour, Perfo, Type
from .forms import AdaptForm
from django.db.models import Sum, Avg, Max, Min, Count, Q
from . import test
from . import graph
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

def agrperfo(qset, stat="sum", div=3): # calcul des résultats agrégés (perfo) + mise en forme
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
    # mise en forme
    res_form={k:fmt_dct(k, v) for k , v in res.items() }
    return(res_form)

def comp_today(): # comparaison à la date actuelle  
    dt=datetime.date.today()
    flt=Q(Date__month__lt=dt.month)|(Q(Date__day__lte=dt.day)&Q(Date__month=dt.month))
    data_comp = Perfo.objects.filter(flt)
    tours = BikeTour.objects.filter(Type__in=[1, 2]).values_list('id', flat=True)
    stat_comp_act=agrperfo(data_comp.filter(Q(Date__year=dt.year)&Q(Refparcours__in = tours)), stat="sum")
    stat_comp_act_last=agrperfo(data_comp.filter(Q(Date__year__gte=(dt.year-3))&Q(Date__year__lt=dt.year)&Q(Refparcours__in = tours)), stat="avg_sub",  div=3)
    stat_comp = {"dt":dt,
                 "act":stat_comp_act,
                 "last":stat_comp_act_last,
                 "data":data_comp}
    return(stat_comp)
    
def comp_any(qset, y=None): # autres comparaisons, comp gérée lors de la création de qset ! 
    if y is None:
        dt=datetime.date.today()
    else:
        dt=datetime.date(int(y),1,1)
    data_comp = qset
    tours = BikeTour.objects.filter(Type__in=[1, 2]).values_list('id', flat=True)
    stat_comp_act=agrperfo(data_comp.filter(Q(Date__year=dt.year)&Q(Refparcours__in = tours)), stat="sum")
    stat_comp_act_last=agrperfo(data_comp.filter(Q(Date__year__gte=(dt.year-3))&Q(Date__year__lt=dt.year)&Q(Refparcours__in = tours)), stat="avg_sub",  div=3)
    stat_comp = {"dt":dt,
                 "act":stat_comp_act,
                 "last":stat_comp_act_last,
                 "data":data_comp}
    return(stat_comp)
   

##### Listes de choix

def index(request):
    lst_link = {"Tours":"biketours/tours", "Statistiques":"biketours/stat", "Graphiques":"biketours/graph", 
                "Introduction données":"biketours/input", "Tests":"biketours/tests"}
    stat_comp = comp_today()
    context = {"lst_link":lst_link,
               "dt":stat_comp["dt"],
               "stat_comp_act":stat_comp["act"],
               "stat_comp_act_last":stat_comp["last"]}
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

def det_perf(request, perf_id): ## A DEVELOPPER : QUE MONTRER ??? AUTRES PERFORMANCES LIEES AU MEME TOUR ???
    perf = Perfo.objects.get(pk=perf_id)
    perf_old = agrperfo(Perfo.objects.filter(Refparcours=perf.Refparcours), stat="avg")
    if request.method == "POST":
        form = AdaptForm(request.POST, instance=perf) # instance = ... permet de mettre à jour une données existante !
    else:
        form = AdaptForm(initial={"Refparcours" : perf.Refparcours,
                                  "Remarques" : perf.Remarques}, instance=perf)
               # initial = ... permet de de donner des valeurs initiales (ici celles de perf) !
        
    if form.is_valid(): 
        form.save()
            
    context = {"perf":perf,
               "perf_old":perf_old,
               "form":form}
    return render(request, "biketours/det_perf.html" ,context)

##### 2. Statistiques
    
## Stats comparaison jour 
    
def stat_comp(request):
    
    # valeurs totales : année en cours + moyenne 3 dernières années
    stat_comp = comp_today()
    
    # valeurs par activité, par année
    stat_comp_act_y = dict()
    for t in Type.objects.values_list("pk", flat=True) :
        tours = BikeTour.objects.filter(Type=t).values_list('id', flat=True).order_by('id')
        data_comp_y = stat_comp["data"].filter(Refparcours__in = tours)
        tmp=dict()
        for y in Perfo.objects.dates("Date", "year", order="DESC") :
            data_comp_act_y = data_comp_y.filter(Date__year=y.year)
            tmp[y.year]= agrperfo(data_comp_act_y, stat="sum")
        stat_comp_act_y[Type.objects.get(pk=t).Type] = tmp
        
    context = {
               "dt":stat_comp["dt"],
               "stat_comp_act":stat_comp["act"],
               "stat_comp_act_last":stat_comp["last"],
               "stat_comp_act_y":stat_comp_act_y}
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
    stat_comp=comp_any(data_y)
        
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
    stat_comp=comp_any(Perfo.objects.all(), y=year_id)
    
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
    tours = BikeTour.objects.filter(Type=act_id)
    tours = tours.values_list('id', flat=True).order_by('id')
    data_act = Perfo.objects.filter(Refparcours__in = tours)
    stat_comp=comp_any(data_act)
        
    # valeurs par activité, par année
    stat_act_y = dict()
    for y in Perfo.objects.dates("Date", "year", order="DESC") :
        data_act_y = data_act.filter(Date__year=y.year)
        stat_act_y[y.year] = agrperfo(data_act_y, stat="sum")
    
    context = {
               "stat_comp_act":stat_comp["act"],
               "stat_comp_act_last":stat_comp["last"],
               "stat_act_y":stat_act_y,
               "act":Type.objects.get(pk=act_id)}
    return render(request, "biketours/stat_act.html", context)

#### 3. Graph A DEVELOPPER !!!
    
def graph_year(request):
    title="Totaux annuels"
    image = 'comp_y.png'
    context = {"image":image,
               "title":title}
    return render(request, "biketours/graph.html" ,context)

def graph_month(request):
    title="Mois courant"
    image = 'comp_m.png'
    context = {"image":image,
               "title":title}
    return render(request, "biketours/graph.html" ,context)

def graph_comp(request):
    title="Comparaison date actuelle"
    data=graph.prepa_data()
    gr=graph.gr_courant(data)
    image = 'comp_date.png'
    context = {"image":image,
               "title":title,
               "gr":gr,
               "data":data}
    return render(request, "biketours/graph.html" ,context)

    
#def showimage(request):
#    # Construct the graph
#    t = arange(0.0, 2.0, 0.01)
#    s = sin(2*pi*t)
#    plot(t, s, linewidth=1.0)
# 
#    xlabel('time (s)')
#    ylabel('voltage (mV)')
#    title('About as simple as it gets, folks')
#    grid(True)
# 
#    # Store image in a string buffer
#    buffer = StringIO.StringIO()
#    canvas = pylab.get_current_fig_manager().canvas
#    canvas.draw()
#    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
#    pilImage.save(buffer, "PNG")
#    pylab.close()
# 
#    # Send buffer in a http response the the browser with the mime type image/png set
#    return HttpResponse(buffer.getvalue(), content_type="image/png")

##### 4. Input données

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


# exemple
#def upload_csv(request):
#	data = {}
#	if "GET" == request.method:
#		return render(request, "myapp/upload_csv.html", data)
#    # if not GET, then proceed
#	try:
#		csv_file = request.FILES["csv_file"]
#		if not csv_file.name.endswith('.csv'):
#			messages.error(request,'File is not CSV type')
#			return HttpResponseRedirect(reverse("myapp:upload_csv"))
#        #if file is too large, return
#		if csv_file.multiple_chunks():
#			messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
#			return HttpResponseRedirect(reverse("myapp:upload_csv"))
#
#		file_data = csv_file.read().decode("utf-8")		
#
#		lines = file_data.split("\n")
#		#loop over the lines and save them in db. If error , store as string and then display
#		for line in lines:						
#			fields = line.split(",")
#			data_dict = {}
#			data_dict["name"] = fields[0]
#			data_dict["start_date_time"] = fields[1]
#			data_dict["end_date_time"] = fields[2]
#			data_dict["notes"] = fields[3]
#			try:
#				form = EventsForm(data_dict)
#				if form.is_valid():
#					form.save()					
#				else:
#					logging.getLogger("error_logger").error(form.errors.as_json())												
#			except Exception as e:
#				logging.getLogger("error_logger").error(repr(e))					
#				pass
#
#	except Exception as e:
#		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
#		messages.error(request,"Unable to upload file. "+repr(e))
#
#	return HttpResponseRedirect(reverse("myapp:upload_csv"))
    
##### 5. Tests

def tests(request):
    a = test.niet()
    context = {"a":a}
    return render(request, "biketours/tests.html" ,context)