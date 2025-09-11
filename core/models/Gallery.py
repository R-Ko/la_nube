from django.db import models
from django_resized import ResizedImageField
from django.core.exceptions import ValidationError
from core.models.ClassGroup import ClassGroup

class Gallery(models.Model):
    classgroup = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, null=True)
    image = ResizedImageField(size=[300, 300], upload_to='classgroups_images/', blank=True, null=True)
    date = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.classgroup}"
    
    def clean(self):
        # Validar que no se exceda el límite de 110 elementos por galería
        if self.classgroup:
            count = Gallery.objects.filter(classgroup=self.classgroup).count()
            if count >= 110:
                raise ValidationError("No se pueden agregar más de 110 fotos/videos a esta galería.")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)
    
    class Meta:
        managed = True
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'