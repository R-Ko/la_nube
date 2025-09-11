from django.db.models.query import QuerySet
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, FormView
from core.models.Professor import Professor
from core.forms import ProfessorForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.models.User import UserApp
from django.contrib.auth.models import User, Group
from django.template import loader
from django.shortcuts import render, get_object_or_404 

class ProfessorCreateView(LoginRequiredMixin, CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = "core/professor_form.html"

    def get_success_url(self):
        return reverse("core:professor-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ProfessorCreateView, self).form_invalid(form)

    def form_valid(self, form):
        first_name = form.cleaned_data["first_name"]
        nip = form.cleaned_data["nip"]
        
        # Función para limpiar cadenas (quitar acentos, espacios, caracteres especiales)
        import unicodedata
        def clean_string(text):
            # Normalizar para eliminar acentos y convertir a ASCII
            text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
            # Mantener solo caracteres alfanuméricos
            return ''.join(c for c in text if c.isalnum()).lower()
        
        # Limpiar el nombre y el NIP
        clean_name = clean_string(first_name)
        clean_nip = clean_string(str(nip))
        
        # Generar username: nombre limpio + NIP limpio
        base_username = f"{clean_name}{clean_nip}"
        
        # Asegurar que no sea demasiado largo (máximo 150 caracteres)
        username = base_username[:150]
        
        # Verificar que el username sea único
        original_username = username
        counter = 1
        while UserApp.objects.filter(username=username).exists():
            # Si ya existe, agregar un sufijo numérico
            suffix = str(counter)
            username = f"{original_username[:150-len(suffix)]}{suffix}"
            counter += 1
        
        # Validar que el nip no exista en UserApp
        if UserApp.objects.filter(nip=nip).exists():
            form.add_error("nip", "Este NIP ya está registrado en usuarios.")
            return self.form_invalid(form)
        
        # Crear usuario
        user = UserApp.objects.create_user(
            username=username,
            first_name=first_name,
            last_name="",  # No usamos el apellido para el username
            password=username,  # La contraseña es igual al username
            security_question=form.cleaned_data.get("security_question"),
            security_answer=form.cleaned_data.get("security_answer"),
            rol="Profesor",
            nip=nip,
        )
        user.groups.add(Group.objects.get(name="Profesor"))
        
        # Guardar Professor del formulario asociado a ese user
        form.instance.user = user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProfessorCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Educadoras"
        return context

class ProfessorListView(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'core/professor_list.html'

    def get_queryset(self):
        return Professor.objects.filter(active=True).exclude(user__is_staff = True)

    def get_context_data(self, **kwargs):
        context = super(ProfessorListView, self).get_context_data(**kwargs)
        context["title_page"] = "Educadoras"
        return context

class ProfessorEditView(LoginRequiredMixin, UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'core/professor_form.html'
    success_url = reverse_lazy('core:professor-list')

    def form_invalid(self, form):
        print('ERRORS',form.errors)
        return super(ProfessorEditView, self).form_invalid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        u = self.object.user
        initial.update({
            "first_name": u.first_name,
            "last_name": u.last_name,
            "security_question": u.security_question,
            "security_answer": u.security_answer,
            "nip": u.nip,
        })
        return initial

    def form_valid(self, form):
        u = self.object.user
        u.first_name = form.cleaned_data["first_name"]
        u.last_name = form.cleaned_data["last_name"]
        u.security_question = form.cleaned_data.get("security_question")
        u.security_answer = form.cleaned_data.get("security_answer")

        new_nip = form.cleaned_data.get("nip")
        if new_nip and UserApp.objects.exclude(pk=u.pk).filter(nip=new_nip).exists():
            form.add_error("nip", "Este NIP ya está registrado en otro usuario.")
            return self.form_invalid(form)
        u.nip = new_nip
        u.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProfessorEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Educadoras"        
        context["first_name"] = self.object.user.first_name        
        context["last_name"] = self.object.user.last_name
        return context

class ProfessorDeleteView(LoginRequiredMixin, DeleteView):
    model = Professor
    success_url = reverse_lazy('core:professor-list')

    def get_context_data(self, **kwargs):
        context = super(ProfessorDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Educadoras"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Professor.objects.get(pk=int(kwargs['pk']))
        p.active = False
        p.save()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "El profesor ha sido eliminado.")
        return HttpResponseRedirect(success_url)
    
class ProfessorDetailView(LoginRequiredMixin, DetailView):
    model = Professor
    template_name = 'core/professor_details.html' 

    def get_context_data(self, **kwargs):
        context = super(ProfessorDetailView, self).get_context_data(**kwargs)
        context["title_page"] = "Mi Perfil"
        return context 
    
def profile_professor(request, pk):
    professor = get_object_or_404(Professor, user__username=pk)  # Busca por username
    context = {
        "title_page": "Mi Perfil",
        "object": professor
    }
    template = loader.get_template('core/professor_details.html')
    return HttpResponse(template.render(context, request))

class ProfessorListHistoryView(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'core/professor_history.html'

    def get_queryset(self):
        return Professor.objects.filter(active=False).exclude(user__is_staff = True)

    def get_context_data(self, **kwargs):
        context = super(ProfessorListHistoryView, self).get_context_data(**kwargs)
        context["title_page"] = "Educadoras Histórico"
        return context