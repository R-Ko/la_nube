from django.db import models
from django.conf import settings
from .Child import Child
import datetime
import django.utils.timezone

CURRENCY = [
    ('USD', 'USD'),
    ('Euro', 'Euro'),
    ('MLC', 'MLC'),
    ('USA Zelle', 'USA Zelle')
]

MONTHS = [
    ('Enero', 'Enero'),
    ('Febrero', 'Febrero'),
    ('Marzo', 'Marzo'),
    ('Abril', 'Abril'),
    ('Mayo', 'Mayo'),
    ('Junio', 'Junio'),
    ('Julio', 'Julio'),
    ('Agosto', 'Agosto'),
    ('Septiembre', 'Septiembre'),
    ('Octubre', 'Octubre'),
    ('Noviembre', 'Noviembre'),
    ('Diciembre', 'Diciembre'),
]


def get_year_choices():
    current_year = datetime.datetime.now().year
    return [(y, y) for y in range(current_year - 3, current_year + 4)]


class Bill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    paid = models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name="Niño/a")  # Parent paid
    date = models.DateField(default=django.utils.timezone.now)
    month = models.CharField(
        max_length=50, 
        choices=MONTHS, 
        verbose_name="Mes",
        default=MONTHS[datetime.datetime.now().month - 1][0]
    )
    year = models.IntegerField(
        choices=get_year_choices(), 
        verbose_name="Año", 
        default=datetime.datetime.now().year
    )
    currency = models.CharField(max_length=50, choices=CURRENCY, verbose_name="Moneda", default="USD")
    amount = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.paid} ({self.month} {self.year})"

    class Meta:
        managed = True
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'
        unique_together = (("paid", "month", "year"),)
