from django.db import models
from .Child import Child

STATUS = [
    ('Aprobado', 'Aprobado'),
    ('Pendiente', 'Pendiente'),
    ('Rechazado', 'Rechazado'),
]

class Family(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(null=True)
    ic = models.CharField(max_length=50, null=True)
    relationship = models.CharField(max_length=50)    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=50, choices=STATUS, null = True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Family'
        verbose_name_plural = 'Familys'
        unique_together = (("ic", "child"),)