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
def save_parent_professor(sender, instance, **kwargs):
    try:
        if instance.rol == "Progenitor":
            instance.groups.add(Group.objects.get(name="Progenitor"))
            if not Parent.objects.filter(nip=instance.nip).exists():
                parent = Parent(user=instance, nip=instance.nip, is_mother=True if instance.mother else False)
                parent.save()
            else:
                parent = Parent.objects.get(nip=instance.nip)
                parent.user = instance
                parent.save()

        elif instance.rol == "Profesor":
            instance.groups.add(Group.objects.get(name="Profesor"))
            if not Professor.objects.filter(user=instance).exists():
                Professor.objects.create(user=instance, nip=instance.nip)

        elif instance.rol == "Admin":
            instance.is_staff = True
            instance.groups.add(Group.objects.get(name="Admin"))
            instance.save()

        elif instance.rol == "Supervisor":
            instance.groups.add(Group.objects.get(name="Supervisor"))
            if not Professor.objects.filter(user=instance).exists():
                Professor.objects.create(user=instance, is_supervisor=True)
    except:
        pass

@receiver(post_save, sender=UserApp)
def force_password_change_new_user(sender, instance, created, **kwargs):
    if created:  # Solo cuando es nuevo
        instance.must_change_password = True
        instance.save()


