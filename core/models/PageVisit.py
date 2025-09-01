from django.db import models
from django.utils import timezone
from django.conf import settings


class PageVisit(models.Model):
    visit_count = models.IntegerField(default=0)
    last_visited = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        # return f"{self.url}: {self.visit_count} visits"
        return self.ip_address
    
    class Meta:
        managed = True
        verbose_name = 'PageVisit'
        verbose_name_plural = 'PageVisits'