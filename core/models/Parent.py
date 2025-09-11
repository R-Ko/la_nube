from django.db import models
from django.conf import settings


SCHOOL_LEVEL = [
    ('Primaria', 'Primaria'),
    ('Secundaria', 'Secundaria'),
    ('Técnica y Profesional', 'Técnica y Profesional'),
    ('Medio Superior', 'Medio Superior'),
    ('Superior', 'Superior'),
]

class Parent(models.Model):
    user = models.OneToOneField("UserApp", on_delete=models.CASCADE, related_name="parent")
    first_name = models.CharField(max_length=50, verbose_name="Nombre", null=True)
    last_name = models.CharField(max_length=50, verbose_name="Apellidos", null=True)
    #nip = models.CharField(max_length=50, verbose_name="NIP", null=True, unique = False)
    # date_birth = models.DateField(verbose_name="Fecha de nacimiento", null=True)
    address = models.CharField(max_length=200, verbose_name="Dirección", null=True)
    phone = models.CharField(max_length=50, verbose_name="Teléfono", null=True)
    # school_level = models.CharField(max_length=50, choices=SCHOOL_LEVEL, verbose_name="Nivel escolar", null=True, blank=True)
    # work_center = models.CharField(max_length=1000, verbose_name="Centro de trabajo", null=True, blank=True)
    # position = models.CharField(max_length=1000, verbose_name="Cargo", null=True, blank=True)
    illnesses = models.CharField(max_length=1000, verbose_name="Enfermedades que padece", null=True)
    alcoholism = models.BooleanField(verbose_name="Alcoholismo", null=True)
    smoking = models.BooleanField(verbose_name="Tabaquismo", null=True)
    is_mother = models.BooleanField(null=True)
    life = models.BooleanField(null=True)
    active = models.BooleanField(default=True)
    can_pickup = models.BooleanField(default=False)

    def __str__(self):
        first_name = self.first_name if self.first_name else ''
        last_name = self.last_name if self.last_name else ''
        return f"{first_name} {last_name}"

    class Meta:
        managed = True
        verbose_name = 'Parent'
        verbose_name_plural = 'Parents'