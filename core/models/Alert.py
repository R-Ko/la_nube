from django.db import models
from django.conf import settings


class Alert(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    publish = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'