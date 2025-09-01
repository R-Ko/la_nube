from django.db import models
from .Child import Child

TYPES = [
    ('Salud', 'Salud'),
    ('Logros', 'Logros'),
]

class ReportChild(models.Model):
    note = models.TextField(verbose_name="Resumen")
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TYPES)
    date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.note} ({self.type})"

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'ReportChild'
        verbose_name_plural = 'ReportChilds'