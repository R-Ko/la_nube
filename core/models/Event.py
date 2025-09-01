from django.db import models
from django.conf import settings


AGE_RANGE = [
    ('1 a 3 años', '1 a 3 años'),
    ('3 a 5 años', '3 a 5 años'),
    ('más de 5 años', 'más de 5 años'),
]

class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=50, verbose_name="Nombre")
    description = models.CharField(max_length=50, verbose_name="Descripción")
    age_range = models.CharField(max_length=50, choices=AGE_RANGE)
    cover = models.ImageField()

    def __str__(self):
        return f"{self.name} ({self.date})"

    class Meta:
        managed = True
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        unique_together = (("name", "date"),)