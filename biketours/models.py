from django.db import models

class But(models.Model):
    But = models.CharField(max_length=250, default=None)
    Descriptif = models.CharField(max_length=1000, default=None, blank=True, null=True)
            
    def __str__(self): 
        # représentation de l'objet si print => permet ici d'afficher But dans les autres tables liées et également sur liens url
        return(self.But)
    
class Type(models.Model):
    Type = models.CharField(max_length=250, default=None)
    Descriptif = models.CharField(max_length=1000, default=None, blank=True, null=True)
            
    def __str__(self): 
        # représentation de l'objet si print => permet ici d'afficher Type dans les autres tables liées et également sur liens url
        return(self.Type)

class BikeTour(models.Model):
    Parcours = models.CharField(max_length=250, default=None)
    Variante = models.CharField(max_length=250, default=None, blank=True, null=True)
    But = models.ForeignKey(But, on_delete=models.CASCADE)
    Type = models.ForeignKey(Type, on_delete=models.CASCADE)
    Descriptif = models.CharField(max_length=1000, default=None, blank=True, null=True)
        
    # Caractéristiques partiels 1 - 10 :
    Descr_part_1 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_1 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_1 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_2 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_2 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_2 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_3 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_3 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_3 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_4 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_4 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_4 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_5 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_5 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_5 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_6 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_6 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_6 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_7 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_7 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_7 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_8 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_8 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_8 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_9 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_9 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_9 = models.FloatField(default=None, blank=True, null=True)
    Descr_part_10 = models.CharField(max_length=250, default=None, blank=True, null=True)
    Dist_part_10 = models.FloatField(default=None, blank=True, null=True)
    Deniv_part_10 = models.FloatField(default=None, blank=True, null=True)
    
    def __str__(self): 
        # représentation de l'objet si print => permet ici d'afficher Parcours - Variante dans les autres tables liées et également sur liens url
        if self.Variante is None:
            return(self.Parcours)
        else :    
            return(self.Parcours + " - " + self.Variante)
            
    def title(self):
        if self.Variante is None:
            return(self.Parcours)
        else :    
            return(self.Parcours + " - " + self.Variante)
 
class Perfo(models.Model):
    Refparcours = models.ForeignKey(BikeTour, blank=True, null=True, on_delete=models.CASCADE)
           # on_delete=models.CASCADE : Perfo effacée si BikeTour effacé !
           # blank=True, null=True : autorisé pour permettre importation de tours sans référence Refparcours
    Date = models.DateField(default=None)    
    Distance = models.FloatField(default=None)
    Temps = models.DurationField(default=None)
    Remarques = models.CharField(max_length=1000, default=None, blank=True, null=True)
    Dénivelé = models.FloatField(default=None, blank=True, null=True)
    Vitesse_max = models.FloatField(default=None, blank=True, null=True)
    FC_moy = models.FloatField(default=None, blank=True, null=True)
    FC_max = models.FloatField(default=None, blank=True, null=True)
    
    # Temps partiels 1 - 10 :
    Temps_part_1 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_2 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_3 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_4 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_5 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_6 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_7 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_8 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_9 = models.DurationField(default=None, blank=True, null=True)
    Temps_part_10 = models.DurationField(default=None, blank=True, null=True)
    
    def __str__(self): 
        # représentation de l'objet si print => permet ici d'afficher Parcours - Variante dans les autres tables liées et également sur liens url
        return(str(self.Refparcours) + " - " + str(self.Date) + " - " + str(self.Temps)+ " - " + str(self.Distance))

    def moy(self):
        if (self.Distance is None or self.Temps is None) :
            vmoy=None
        else :
            vmoy=round(self.Distance/self.Temps.total_seconds()*3600,2)
        return(vmoy)

