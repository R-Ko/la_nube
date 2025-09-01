from django.db import models
from core.models import Child, Professor
from django.conf import settings


class AssistanceDaily(models.Model):
    child = models.ForeignKey(Child.Child, on_delete=models.CASCADE, null = True)
    professor = models.ForeignKey(Professor.Professor, on_delete=models.CASCADE, null = True)
    date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asistencia diaria de {self.child.name} el {self.date}"