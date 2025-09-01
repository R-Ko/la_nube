from django.db import models
from django.conf import settings
from .Child import Child

class ClassGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre", unique = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    childs = models.ManyToManyField(Child)

    def __str__(self):
        return self.name

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'ClassGroup'
        verbose_name_plural = 'ClassGroups'