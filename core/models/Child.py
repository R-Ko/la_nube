from django.db import models
from django_resized import ResizedImageField
from core.models.Parent import Parent

SEX = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
]

class Child(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nip = models.CharField(max_length=50)
    date_birth = models.DateField()
    address = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=SEX)
    health_requirements = models.TextField()
    food_requirements = models.TextField()
    periodic_medications = models.TextField()
    observations = models.TextField()
    exp = models.IntegerField()
    image = ResizedImageField(size=[300, 300],upload_to='child_images/', blank=True, null=True, max_length=1000)
    active = models.BooleanField(default=True)
    mother = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, related_name = "mother")
    father = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, related_name = "father")
    date_down = models.DateField(null=True)
    

    def __str__(self):
        return f"{self.first_name} {self.last_name}" 

    class Meta:
        managed = True
        verbose_name = 'Child'
        verbose_name_plural = 'Childs'
        unique_together = (("nip", "active"),)