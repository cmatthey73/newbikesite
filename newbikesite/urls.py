
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = [
    #re_path(r"^$", include("main.urls")),
    #re_path(r"^biketours", include("biketours.urls")),
    re_path(r"^$", include("biketours.urls")),
    re_path(r"^biketours/", include("biketours.urls")),
    re_path(r"admin/", admin.site.urls)
]
