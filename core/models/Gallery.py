from django.db import models
from django_resized import ResizedImageField
from core.models.ClassGroup import ClassGroup


class Gallery(models.Model):
    classgroup = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, null=True)
    image = ResizedImageField(size=[300, 300],upload_to='classgroups_images/', blank=True, null=True)
    date = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.classgroup}" 

    class Meta:
        managed = True
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'