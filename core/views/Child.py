from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, FormView, TemplateView
from core.models.Child import Child
from core.models.Family import Family
from core.models.Parent import Parent
from core.models.ClassGroup import ClassGroup
from core.models.ReportChild import ReportChild
from core.models.User import UserApp
from core.forms import ChildForm, RelationshipForm, ApprovedForm, ParentForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.db import models
from django import forms
from django.contrib.auth.models import Group
import unicodedata
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.db import IntegrityError


User = get_user_model()

def create_or_get_user_from_parent(form_instance, is_mother=True):
    """Crea un UserApp a partir de los datos del Parent si no existe uno con el mismo NIP"""
    
    # Buscar si ya existe un usuario con ese NIP
    user = User.objects.filter(nip=form_instance.nip).first()
    if user:
        return user
    
    # Crear username único: nombre + nip
    username = f"{form_instance.first_name.lower()}{form_instance.nip}"
    password = f"{form_instance.first_name}{form_instance.nip}"

    # Crear nuevo UserApp con los datos del Parent
    user = User.objects.create_user(
        username=username,
        first_name=form_instance.first_name,
        last_name=form_instance.last_name,
        email=form_instance.email if hasattr(form_instance, "email") else None,
        password=password,
        nip=form_instance.nip,
    )

    # Asignar grupo de progenitor
    progenitor_group, _ = Group.objects.get_or_create(name="Progenitor")
    user.groups.add(progenitor_group)

    return user


class ChildStepOneCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = ChildForm
    template_name = "core/child_form_one.html"

    def get_success_url(self):
        #pk = self.object.pk
        self.request.session['child_id'] = self.object.pk

        return reverse("core:child-add-two", kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ChildStepOneCreateView, self).form_invalid(form)

    def form_valid(self, form):
     if Child.objects.filter(nip=form.instance.nip, active=False).exists():
        messages.add_message(self.request, messages.SUCCESS, "Este niño se encuentra en el histórico. Debe eliminarlo definitivamente y agregarlo nuevamente.")
        return super().form_invalid(form)

     if Child.objects.filter(nip=form.instance.nip, active=True).exists():
        messages.add_message(self.request, messages.SUCCESS, "Ya existe un niño con este NIP.")
        return super().form_invalid(form)

     last_exp = Child.objects.all().order_by('-id').first()
     form.instance.exp = last_exp.exp + 1 if last_exp else 1

     response = super().form_valid(form)  # Guardamos primero el objeto
     self.request.session['child_id'] = self.object.pk  # Ahora se ejecuta correctamente
     return response

    def get_context_data(self, **kwargs):
        context = super(ChildStepOneCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Niños"
        return context
    
class ChildStepTwoCreateView(LoginRequiredMixin, CreateView):
    """Vista para registrar la madre"""
    model = Parent
    form_class = ParentForm
    template_name = "core/child_form_two.html"
    
    def get_success_url(self):
        return reverse("core:child-add-three", kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        form.instance.is_mother = True
        form.instance.created_by = self.request.user
        
        # Obtener el NIP del formulario
        nip = form.cleaned_data.get('nip')
        
        # 🔹 Buscar si ya existe usuario con este nip
        user = UserApp.objects.filter(nip=nip).first()
        if not user:
            # Generar username y contraseña
            username = f"{form.cleaned_data['first_name'].lower()}{nip}"
            password = f"{form.cleaned_data['first_name']}{nip}"
            user = UserApp.objects.create_user(
                username=username,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=password,
                nip=nip
            )
            progenitor_group, _ = Group.objects.get_or_create(name="Progenitor")
            user.groups.add(progenitor_group)
        
        # Asignar el usuario al Parent
        form.instance.user = user
        
        # 🔹 Buscar madre existente por nip (a través del usuario)
        parent = Parent.objects.filter(user__nip=nip, is_mother=True).first()
        if parent is None:
            obj = super().form_valid(form)
            id_parent = form.instance.id
        else:
            # actualizar madre existente
            parent.first_name = form.cleaned_data['first_name']
            parent.last_name = form.cleaned_data['last_name']
            parent.address = form.cleaned_data['address']
            parent.phone = form.cleaned_data['phone']
            parent.illnesses = form.cleaned_data['illnesses']
            parent.alcoholism = form.cleaned_data['alcoholism']
            parent.smoking = form.cleaned_data['smoking']
            parent.life = form.cleaned_data['life']
            # 🔹 Agregar el campo can_pickup
            parent.can_pickup = form.cleaned_data.get('can_pickup', False)
            if not parent.user:
                parent.user = user
            parent.save()
            id_parent = parent.id
            # 🔹 Vincular madre al niño (aunque ya existiera)
            child_id = self.request.session.get('child_id')
            child = Child.objects.get(pk=child_id)
            child.mother_id = id_parent
            child.save()
            return HttpResponseRedirect(self.get_success_url())
        
        # 🔹 Vincular madre al niño
        child_id = self.request.session.get('child_id')
        child = Child.objects.get(pk=child_id)
        child.mother_id = id_parent
        child.save()
        return obj
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_page"] = "Niños"
        context["pk"] = self.kwargs.get('pk')
        parent = Parent.objects.filter(user=self.request.user, is_mother=True).first()
        context["parent"] = parent
        # 🔹 Agregar etiqueta para el checkbox
        context["pickup_label"] = "¿Puede recoger al niño?"
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        parent = Parent.objects.filter(user=self.request.user, is_mother=True).first()
        if parent:
            # Obtenemos el nip del usuario asociado al parent
            nip = parent.user.nip if parent.user else ''
            initial.update({
                'nip': nip,
                'first_name': parent.first_name,
                'last_name': parent.last_name,
                'address': parent.address,
                'phone': parent.phone,
                'illnesses': parent.illnesses,
                'alcoholism': parent.alcoholism,
                'smoking': parent.smoking,
                'life': parent.life,
                # 🔹 Agregar el valor inicial de can_pickup
                'can_pickup': parent.can_pickup,
            })
        return initial
         
class ChildStepThreeCreateView(LoginRequiredMixin, CreateView):
    """Vista para registrar el padre"""
    model = Parent
    form_class = ParentForm
    template_name = "core/child_form_three.html"
    
    def get_success_url(self):
        return reverse("core:child-add-four", kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        form.instance.is_mother = False
        form.instance.created_by = self.request.user
        
        # Obtener el NIP del formulario
        nip = form.cleaned_data.get('nip')
        
        # 🔹 Buscar si ya existe usuario con este nip
        user = UserApp.objects.filter(nip=nip).first()
        if not user:
            # Generar username y contraseña
            username = f"{form.cleaned_data['first_name'].lower()}{nip}"
            password = f"{form.cleaned_data['first_name']}{nip}"
            user = UserApp.objects.create_user(
                username=username,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=password,
                nip=nip
            )
            progenitor_group, _ = Group.objects.get_or_create(name="Progenitor")
            user.groups.add(progenitor_group)
        
        # Asignar el usuario al Parent
        form.instance.user = user
        
        # 🔹 Buscar padre existente por nip (a través del usuario)
        parent = Parent.objects.filter(user__nip=nip, is_mother=False).first()
        if parent is None:
            obj = super().form_valid(form)
            id_parent = form.instance.id
        else:
            # actualizar padre existente
            parent.first_name = form.cleaned_data['first_name']
            parent.last_name = form.cleaned_data['last_name']
            parent.address = form.cleaned_data['address']
            parent.phone = form.cleaned_data['phone']
            parent.illnesses = form.cleaned_data['illnesses']
            parent.alcoholism = form.cleaned_data['alcoholism']
            parent.smoking = form.cleaned_data['smoking']
            parent.life = form.cleaned_data['life']
            # 🔹 Agregar el campo can_pickup
            parent.can_pickup = form.cleaned_data.get('can_pickup', False)
            if not parent.user:
                parent.user = user
            parent.save()
            id_parent = parent.id
            # 🔹 Vincular padre al niño incluso si ya existía
            child_id = self.request.session.get('child_id')
            child = Child.objects.get(pk=child_id)
            child.father_id = id_parent
            child.save()
            return HttpResponseRedirect(self.get_success_url())
        
        # 🔹 Vincular padre al niño (nuevo caso)
        child_id = self.request.session.get('child_id')
        child = Child.objects.get(pk=child_id)
        child.father_id = id_parent
        child.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_page"] = "Niños"
        context["pk"] = self.kwargs.get('pk')
        parent = Parent.objects.filter(user=self.request.user, is_mother=False).first()
        context["parent"] = parent
        # 🔹 Agregar etiqueta para el checkbox
        context["pickup_label"] = "¿Puede recoger al niño?"
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        parent = Parent.objects.filter(user=self.request.user, is_mother=False).first()
        if parent:
            # Obtenemos el nip del usuario asociado al parent
            nip = parent.user.nip if parent.user else ''
            initial.update({
                'nip': nip,
                'first_name': parent.first_name,
                'last_name': parent.last_name,
                'address': parent.address,
                'phone': parent.phone,
                'illnesses': parent.illnesses,
                'alcoholism': parent.alcoholism,
                'smoking': parent.smoking,
                'life': parent.life,
                # 🔹 Agregar el valor inicial de can_pickup
                'can_pickup': parent.can_pickup,
            })
        return initial
      
class ChildStepFourCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = RelationshipForm
    template_name = "core/child_form_four.html"

    def get_success_url(self, *args, **kwargs):
        return reverse("core:child-add-five", kwargs={'pk': self.kwargs['pk']})

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ChildStepFourCreateView, self).form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        if form.instance.first_name == '' and form.instance.last_name == '' and form.instance.age is None:
            return HttpResponseRedirect(self.get_success_url())
        form.instance.created_by = self.request.user
        print(self.request.session)
        form.instance.child_id = self.request.session.get('child_id')
        form.instance.type = "Relationship"
        form.instance.status = None
        return super(ChildStepFourCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ChildStepFourCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Niños"
        context["pk"] = self.kwargs.get('pk')
        return context
    
class ChildStepFiveCreateView(LoginRequiredMixin, CreateView):
    model = Family
    form_class = ApprovedForm
    template_name = "core/child_form_five.html"
    
    def get_success_url(self):
        return reverse("core:child-list")
    
    def form_invalid(self, form):
        print('ERROR', form.errors)
        return super().form_invalid(form)
    
    def form_valid(self, form, *args, **kwargs): 
        if form.instance.first_name == '' and form.instance.last_name == '' and form.instance.ic is None:
            return HttpResponseRedirect(reverse('core:child-list'))      
        
        child_id = self.request.session.get('child_id')
        form.instance.child_id = child_id
        form.instance.type = "Approved"
        form.instance.status = "Aprobado"
        
        # Guardamos el formulario actual
        response = super().form_valid(form)
        
        # Obtener el niño actual
        child = Child.objects.get(pk=child_id)
        
        # Verificar si la madre puede recoger y agregarla si es necesario
        if child.mother and child.mother.can_pickup:
            # Obtener el NIP de la madre a través del usuario
            mother_nip = child.mother.user.nip if child.mother.user else None
            if mother_nip:
                # Usar get_or_create para evitar duplicados
                Family.objects.get_or_create(
                    child=child,
                    ic=mother_nip,
                    defaults={
                        'type': "Approved",
                        'status': "Aprobado",
                        'relationship': "Madre",
                        'first_name': child.mother.first_name,
                        'last_name': child.mother.last_name,
                    }
                )
        
        # Verificar si el padre puede recoger y agregarlo si es necesario
        if child.father and child.father.can_pickup:
            # Obtener el NIP del padre a través del usuario
            father_nip = child.father.user.nip if child.father.user else None
            if father_nip:
                # Usar get_or_create para evitar duplicados
                Family.objects.get_or_create(
                    child=child,
                    ic=father_nip,
                    defaults={
                        'type': "Approved",
                        'status': "Aprobado",
                        'relationship': "Padre",
                        'first_name': child.father.first_name,
                        'last_name': child.father.last_name,
                    }
                )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_page"] = "Niños"
        context["pk"] = self.kwargs.get('pk')
        
        # Obtener el niño actual
        child_id = self.request.session.get('child_id')
        child = Child.objects.get(pk=child_id)
        
        # Agregar información sobre los progenitores que pueden recoger
        context["mother_can_pickup"] = child.mother.can_pickup if child.mother else False
        context["father_can_pickup"] = child.father.can_pickup if child.father else False
        
        return context

@csrf_exempt
@require_http_methods(['POST'])
def save_relationship(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    age = request.POST.get('age')
    relationship = request.POST.get('relationship')
    # Aqui puedes volver a tomar del POST
    child = request.session.get('child_id')

    relationship_obj = Family.objects.create(
        type="Relationship",        
        relationship=relationship,
        first_name=first_name,
        last_name=last_name,
        age=age,
        child_id = child
    )
    return JsonResponse({'message': 'Relationship saved successfully'})

@csrf_exempt
@require_http_methods(['POST'])
def save_approved(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    ic = request.POST.get('ic')
    relationship = request.POST.get('relationship')
    # Aqui puedes volver a tomar del POST
    child = request.session.get('child_id')

    # save the relationship to the database
    # assuming you have a model called Relationship
    relationship_obj = Family.objects.create(
        type="Approved",        
        status="Aprobado",
        relationship=relationship,
        first_name=first_name,
        last_name=last_name,
        ic=ic, 
        child_id = child
    )
    return JsonResponse({'message': 'Approved saved successfully'})
    
class ChildDetailView(LoginRequiredMixin, DetailView):
    model = Child
    template_name = 'core/child_details.html'

    def get_context_data(self, **kwargs):
        context = super(ChildDetailView, self).get_context_data(**kwargs)
        context["title_page"] = "Perfil Infantil"
        context["mother"] = Child.objects.get(id = self.object.id).mother
        context["classgroup"] = ClassGroup.objects.filter(childs = self.object)
        context["father"] = Child.objects.get(id = self.object.id).father
        context["family_approved"] = Family.objects.filter(child = self.object.id, type="Approved").exclude(ic__in=['', None])
        context["familys"] = Family.objects.filter(child = self.object.id).exclude(age=None)
        context["last_report"] = ReportChild.objects.filter(child = self.object.id).order_by('-date').first()
        return context 



class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'core/child_list.html'
    paginate_by = 12


    def get_queryset(self):
        user = self.request.user
        queryset = Child.objects.filter(active=True)

        search_query = self.request.GET.get('search')
        if search_query:
            search_query = search_query.strip()
            if search_query:
                queryset = queryset.annotate(
                    full_name=Concat('first_name', Value(' '), 'last_name')
                ).filter(
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query) |
                    Q(full_name__icontains=search_query)
                )

        if user.is_superuser or user.groups.filter(name__in=["Supervisor", "Profesor", "Admin"]).exists():
            return queryset

        parent = Parent.objects.filter(user=user).first()
        if parent:
            return queryset.filter(Q(mother=parent) | Q(father=parent))

        return queryset.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_page"] = "Niños"
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ChildEditView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildForm
    template_name = "core/child_form_edit.html"

    def get_success_url(self):
        return reverse("core:child-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ChildEditView, self).form_invalid(form)

    def form_valid(self, form):
        # form.instance.father_id = self.request.POST['father']        
        # form.instance.mother_id = self.request.POST['mother']
        form.instance.created_by = self.request.user
        return super(ChildEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ChildEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Niños"
        # context["fathers"] = Parent.objects.filter(active = True, is_mother = False)
        # context["mothers"] = Parent.objects.filter(active = True, is_mother = True)
        return context
    
class ChildDeleteView(LoginRequiredMixin, DeleteView):
    model = Child

    def get_context_data(self, **kwargs):
        context = super(ChildDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Niños"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Child.objects.get(pk=int(kwargs['pk']))
        if p.active:             
            p.active = False
            p.date_down = datetime.now()
            p.save() 
            # Delete families
            families = Family.objects.filter(child = p)
            for family in families:
                family.delete()
            # Delete parents
            if p.father:
                if not Child.objects.filter(father = p.father, active = True).exists():
                    p.father.active = False
                    p.father.save()
            if p.mother:
                if not Child.objects.filter(mother = p.mother, active = True).exists():
                    p.mother.active = False
                    p.mother.save()  
            success_url = reverse_lazy('core:child-list')              
            messages.add_message(request, messages.SUCCESS, "Se ha desmatriculado de manera satisfactoria.")
        else:
            if p.father:
                if not Child.objects.filter(father = p.father, active = True).exists():
                    p.father.delete()
            if p.mother:
                if not Child.objects.filter(mother = p.mother, active = True).exists():
                    p.mother.delete()  
            p.delete()            
            success_url = reverse_lazy('core:child-history')   
            messages.add_message(request, messages.SUCCESS, "Se ha eliminado de manera satisfactoria.")
        return HttpResponseRedirect(success_url)
    
class ChildListHistoryView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'core/child_history.html'
    paginate_by = 12

    def get_queryset(self):
        return Child.objects.filter(active=False)

    def get_context_data(self, **kwargs):
        context = super(ChildListHistoryView, self).get_context_data(**kwargs)
        context["title_page"] = "Niños Históricos"
        return context