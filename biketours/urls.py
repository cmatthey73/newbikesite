from django.urls import include, re_path
from . import views

urlpatterns = [
    ## sommaires
    re_path(r"^$", views.index),
    re_path(r"^tours/$", views.index_tours, name="index_tours"),
    re_path(r"^graph/$", views.index_graph, name="index_graph"),
    re_path(r"^stat/$", views.index_stat, name="index_stat"),
    re_path(r"^list/$", views.index_list, name="index_list"),
    ## performances
    # objectif : lier aux tours et afficher perf liées !!!
    re_path(r"^tours/(?P<tour_id>[0-9]+)/$", views.perf_tours, name="perf_tours"),
	 # (?P<tour_id>[0-9]+) permet de capturer une suite de chiffres présente dans l'url au niveau biketours/... dans la variable tour_id
    re_path(r"^tours/[0-9]+/(?P<perf_id>[0-9]+)/$", views.det_perf, name="det_perf"),
	 # (?P<perf_id>[0-9]+) permet de capturer une suite de chiffres présente dans l'url au niveau biketours/tour_id/... dans la variable perf_id
    
    ## stats
    re_path(r"^stat/year/$", views.years, name="year"),
    re_path(r"^stat/year/(?P<year_id>[0-9]+)/$", views.stat_year, name="stat_year"),
    re_path(r"^stat/month/$", views.month, name="month"),
    re_path(r"^stat/month/(?P<mth_id>[0-9]+)/$", views.stat_month, name="stat_month"),
    re_path(r"^stat/act/$", views.activ, name="stat_act"),
    re_path(r"^stat/act/(?P<act_id>[0-9]+)/$", views.stat_act, name="stat_act"),
    re_path(r"^stat/comp/$", views.stat_comp, name="stat_comp"),
    
    ## graph
    re_path(r"^graph/year/$", views.graph_year, name="graph_year"),
    re_path(r"^graph/month/$", views.graph_month, name="graph_month"),
    re_path(r"^graph/comp/$", views.graph_comp, name="graph_comp"),
    
    ## listes
    re_path(r"^list/month/$", views.month, name="month"),
    re_path(r"^list/month/(?P<mth_id>[0-9]+)/$", views.list_m, name="list_m"),
    re_path(r"^list/act/$", views.list_act, name="list_act"),
    
    ## intro
    re_path(r"^input/$", views.datainput, name="datainput"),
    
    ## tests
    re_path(r"^tests/$", views.tests, name="tst"),
    
]


