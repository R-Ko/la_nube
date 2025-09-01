from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, FormView
from core.models.Family import Family
from core.models.Child import Child
from core.models.Parent import Parent
from core.forms import FamilyForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.contrib.auth.models import User, Group
from django.db.models import QuerySet
from django.db import models

class FamilyCreateView(LoginRequiredMixin, CreateView):
    model = Family
    form_class = FamilyForm
    template_name = "core/family_form.html"

    def get_success_url(self):
        return reverse("core:family-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(FamilyCreateView, self).form_invalid(form)

    def form_valid(self, form):
        child_id = self.request.POST.get("child") or self.request.GET.get("child")
        if not child_id:
            raise ValueError("Debe indicar el niño al que se asignará el familiar.")
        form.instance.child_id = child_id
        form.instance.created_by = self.request.user

        if 'approved' in self.request.POST:
            form.instance.type = "Approved"
            form.instance.status = "Pendiente"
        else:
            form.instance.type = "Relationship"
            form.instance.status = "Pendiente"

        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(FamilyCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Familiares"
        if self.request.user.is_staff:
            context["childs"] = Child.objects.filter(active=True)
        else:
            parent = Parent.objects.get(user=self.request.user)
            context["childs"] = Child.objects.filter(active=True).filter(
            models.Q(mother__nip=parent.nip) | models.Q(father__nip=parent.nip))
        return context

class FamilyEditView(LoginRequiredMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = "core/family_form.html"

    def get_success_url(self):
        return reverse("core:family-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(FamilyEditView, self).form_invalid(form)

    def form_valid(self, form):
        if 'approved' in self.request.POST:
            form.instance.type = "Approved"
            form.instance.status = "Pendiente"
        else:
            form.instance.type = "Relationship"
        form.instance.child_id = self.request.POST["child"]
        form.instance.created_by = self.request.user
        return super(FamilyEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FamilyEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Familiares"

        if self.request.user.is_staff:
            context["childs"] = Child.objects.filter(active=True)
        else:
            parent = Parent.objects.get(user=self.request.user)
            context["childs"] = Child.objects.filter(active=True).filter(
            models.Q(mother__nip=parent.nip) | models.Q(father__nip=parent.nip))
        return context

class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'core/family_list.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name = "Progenitor").exists():
            parent = Parent.objects.get(user_id = self.request.user.id)
            if parent.is_mother:
                childs = Child.objects.filter(active=True, mother = parent)
                return Family.objects.filter(child__in = childs).exclude(ic__in=['', None])
            else:
                childs = Child.objects.filter(active=True, father = parent)
                return Family.objects.filter(child__in = childs).exclude(ic__in=['', None])
        else:
            return Family.objects.filter(child__active = True).exclude(ic__in=['', None]) 
        
    def get_context_data(self, **kwargs):
        context = super(FamilyListView, self).get_context_data(**kwargs)
        context["title_page"] = "Familiares"
        return context
    
class FamilyDeleteView(LoginRequiredMixin, DeleteView):
    model = Family
    success_url = reverse_lazy('core:family-list')

    def get_context_data(self, **kwargs):
        context = super(FamilyDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Familiares"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Family.objects.get(pk=int(kwargs['pk']))
        p.delete()
        messages.add_message(request, messages.SUCCESS, "El familiar ha sido eliminado definitivamente.")
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)
    
@csrf_exempt
@require_http_methods(['GET'])
def status_approved(request,pk):
    p = Family.objects.get(pk=pk)
    p.status = "Aprobado"
    p.save()
    return HttpResponseRedirect(reverse_lazy('core:family-list'))

@csrf_exempt
@require_http_methods(['GET'])
def status_reject(request,pk):
    p = Family.objects.get(pk=pk)
    p.status = "Rechazado"
    p.save()
    return HttpResponseRedirect(reverse_lazy('core:family-list'))