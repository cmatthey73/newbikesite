from django import forms
from .models import Perfo

class AdaptForm(forms.ModelForm):

    class Meta:
        model = Perfo
        fields = ("Refparcours","Remarques",)