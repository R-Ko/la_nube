from django.db import models
from django.conf import settings
from .Child import Child

class Activity(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    childs = models.ManyToManyField(Child)

    def __str__(self):
        return self.name

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Activity'
        verbose_name_plural = 'Activitys'