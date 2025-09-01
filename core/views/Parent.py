from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, FormView
from core.models.Parent import Parent
from core.models.Child import Child
from core.forms import ParentForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model


UserApp = get_user_model()


    
class ParentCreateView(LoginRequiredMixin, CreateView):
    model = Parent
    form_class = ParentForm
    template_name = "core/parent_form.html"

    def get_success_url(self):
        return reverse("core:parent-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ParentCreateView, self).form_invalid(form)


    def form_valid(self, form):
        child = Child.objects.get(id=self.request.POST['child'])

        # Configurar flags madre/vida
        form.instance.is_mother = 1 if "mother" in self.request.POST else 0
        form.instance.life = 1 if "life" in self.request.POST else 0

        # Tomar NIP desde el form
        nip = form.cleaned_data.get("nip")

        # Validar que el nip no exista en UserApp
        if UserApp.objects.filter(nip=nip).exists():
            form.add_error("nip", "Este NIP ya está en uso.")
            return self.form_invalid(form)

        # Crear usuario asociado al padre
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        username = f"{first_name[:2].lower()}{last_name.replace(' ', '').lower()}"

        user = UserApp.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=username,
            security_question=form.cleaned_data.get("security_question"),
            security_answer=form.cleaned_data.get("security_answer"),
            nip=nip,  # 👈 Guardamos también el nip en UserApp
            rol="Progenitor"
        )
        user.groups.add(Group.objects.get(name="Progenitor"))

        # asignar usuario al padre
        form.instance.user = user
        form.instance.created_by = self.request.user
        form.instance.save()

        # asignar relación con niño
        if "mother" in self.request.POST:
            child.mother = form.instance
        else:
            child.father = form.instance
        child.save()

        return super(ParentCreateView, self).form_valid(form)




    def get_context_data(self, **kwargs):
        context = super(ParentCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Padres"
        context["childs"] = Child.objects.filter(active=True)
        return context

class ParentListView(LoginRequiredMixin, ListView):
    model = Parent
    template_name = 'core/parent_list.html'

    def get_queryset(self):
        return Parent.objects.filter(active = True)

    def get_context_data(self, **kwargs):
        context = super(ParentListView, self).get_context_data(**kwargs)
        context["title_page"] = "Padres"
        return context

class ParentEditView(LoginRequiredMixin, UpdateView):
    model = Parent
    form_class = ParentForm
    template_name = 'core/parent_form.html'

    def get_success_url(self):
        return reverse_lazy('core:parent-details', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        if self.object and self.object.user:
            initial["security_question"] = self.object.user.security_question
            initial["security_answer"] = self.object.user.security_answer
        return initial

    def form_invalid(self, form):
        print('ERRORS', form.errors)
        return super(ParentEditView, self).form_invalid(form)

    def form_valid(self, form):        
        if "mother" in self.request.POST:   
            form.instance.is_mother = 1
        else:
            form.instance.is_mother = 0

        if "life" in self.request.POST:   
            form.instance.life = 1
        else:
            form.instance.life = 0

        user = self.object.user
        if user:
            nip = form.cleaned_data.get("nip")

            # validar que no esté repetido en otro user
            if UserApp.objects.filter(nip=nip).exclude(id=user.id).exists():
                form.add_error("nip", "Este NIP ya está en uso por otro usuario.")
                return self.form_invalid(form)

            # actualizar datos del usuario
            user.nip = nip
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.security_question = form.cleaned_data.get("security_question")
            user.security_answer = form.cleaned_data.get("security_answer")
            user.save()


        if self.request.POST.get("child"):
            child = Child.objects.get(id=self.request.POST['child'])      
            if "mother" in self.request.POST:
                child.mother = form.instance
                child.save()
            else:
                child.father = form.instance
                child.save()

        form.instance.created_by = self.request.user
        return super(ParentEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ParentEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Padres"        
        context["first_name"] = self.object.first_name        
        context["last_name"] = self.object.last_name

        if Child.objects.filter(father=self.kwargs['pk']).exists():
            context["childs"] = Child.objects.filter(father=self.kwargs['pk'], active=True)               
            context["child"] = Child.objects.filter(father=self.kwargs['pk'], active=True)  
        if Child.objects.filter(mother=self.kwargs['pk']).exists():
            context["childs"] = Child.objects.filter(mother=self.kwargs['pk'], active=True)              
            context["child"] = Child.objects.filter(mother=self.kwargs['pk'], active=True)  
        if not Child.objects.filter(father=self.kwargs['pk']).exists() and not Child.objects.filter(mother=self.kwargs['pk']).exists():            
            context["childs"] = Child.objects.filter(active=True) 
        return context


class ParentDeleteView(LoginRequiredMixin, DeleteView):
    model = Parent
        
    def get_context_data(self, **kwargs):
        context = super(ParentDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Padres"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Parent.objects.get(pk=int(kwargs['pk']))
        if p.active:
            p.active = False
            p.save()
            success_url = reverse_lazy('core:parent-list')
            messages.add_message(request, messages.SUCCESS, "El padre ha sido eliminado.")
        else:
            p.delete()            
            success_url = reverse_lazy('core:parent-history')
            messages.add_message(request, messages.SUCCESS, "El padre ha sido eliminado definitivamente.")
        return HttpResponseRedirect(success_url)
    
class ParentDetailView(LoginRequiredMixin, DetailView):
    model = Parent
    template_name = 'core/parent_details.html'    

    def get_context_data(self, **kwargs):
        context = super(ParentDetailView, self).get_context_data(**kwargs)
        context["title_page"] = "Mi Perfil"
        return context 
    
class ParentDetailUserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'core/parent_details.html'    

    def get_context_data(self, **kwargs):
        context = super(ParentDetailUserView, self).get_context_data(**kwargs)
        context["title_page"] = "Mi Perfil"
        return context 
    
def profile_parent(request, pk):
    parent = Parent.objects.get(user_id = pk)
    context = {}
    context["title_page"] = "Mi Perfil"
    context["object"] = parent
    template = loader.get_template('core/parent_details.html')
    return HttpResponse(template.render(context, request))

class ParentListHistoryView(LoginRequiredMixin, ListView):
    model = Parent
    template_name = 'core/parent_history.html'

    def get_queryset(self):
        return Parent.objects.filter(active = False)

    def get_context_data(self, **kwargs):
        context = super(ParentListHistoryView, self).get_context_data(**kwargs)
        context["title_page"] = "Padres Históricos"
        return context
    