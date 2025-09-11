from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models.Professor import Professor
from core.models.Parent import Parent
from django.apps import AppConfig

ROLES = [
    ('Admin', 'Admin'),
    ('Profesor', 'Profesor'),
    ('Progenitor', 'Progenitor'),
    ('Supervisor', 'Supervisor'),
]

class UserApp(AbstractUser): 
    rol = models.CharField(max_length=20, choices=ROLES, default='Admin')
    nip = models.CharField(max_length=20,unique = True)
    security_question =  models.CharField(max_length=30,default="",blank=True,null=True)
    security_answer =  models.CharField(max_length=30,default="",blank=True,null=True)
    mother = models.BooleanField(default = True)       
    terms = models.BooleanField(default = False) 
    must_change_password = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["nip", "email"]
    USERNAME_FIELD = "username"
    
    class Meta:
        managed = True
        verbose_name = 'UserApp'
        verbose_name_plural = 'UsersApp'
        
@receiver(post_save, sender=UserApp, dispatch_uid="save_parent_professor")
def save_parent_professor(sender, instance, created, **kwargs):
    # Importar aquí para evitar importación circular
    from django.contrib.auth.models import Group
    
    try:
        # Solo ejecutar esta lógica si el usuario se acaba de crear
        # o si el rol ha cambiado (esto evita llamadas innecesarias)
        if created:
            if instance.rol == "Progenitor":
                group, _ = Group.objects.get_or_create(name="Progenitor")
                instance.groups.add(group)
                Parent.objects.update_or_create(
                    user=instance,
                    defaults={
                        "is_mother": True if instance.mother else False
                    }
                )
            elif instance.rol == "Profesor":
                group, _ = Group.objects.get_or_create(name="Profesor")
                instance.groups.add(group)
                Professor.objects.get_or_create(user=instance, defaults={"nip": instance.nip})
            elif instance.rol == "Admin":
                instance.is_staff = True
                group, _ = Group.objects.get_or_create(name="Admin")
                instance.groups.add(group)
                # NO LLAMAR A SAVE() AQUÍ PARA EVITAR RECURSIÓN
            elif instance.rol == "Supervisor":
                group, _ = Group.objects.get_or_create(name="Supervisor")
                instance.groups.add(group)
                Professor.objects.get_or_create(user=instance, defaults={"is_supervisor": True})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en save_parent_professor: {e}", exc_info=True)
        raise
    
@receiver(post_save, sender=UserApp)
def force_password_change_new_user(sender, instance, created, **kwargs):
    if created:  # Solo cuando es nuevo
        instance.must_change_password = True
        instance.save()


