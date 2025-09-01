from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.ReportChild import ReportChild
from core.models.Parent import Parent
from core.models.Child import Child
from core.forms import ReportChildForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime

class ReportChildCreateView(LoginRequiredMixin, CreateView):
    model = ReportChild
    form_class = ReportChildForm
    template_name = "core/reportchild_form.html"

    def get_success_url(self):
        return reverse("core:report-all", kwargs={"pk": self.kwargs["pk"]})

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ReportChildCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.child_id = self.request.POST["child"]
        form.instance.user = self.request.user
        return super(ReportChildCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ReportChildCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte Infantil"        
        context["pk"] = self.kwargs.get('pk')
        return context

class ReportChildEditView(LoginRequiredMixin, UpdateView):
    model = ReportChild
    form_class = ReportChildForm
    template_name = "core/reportchild_form.html"

    def get_success_url(self):
        child_pk = self.object.child.pk 
        return reverse("core:report-all", kwargs={"pk": child_pk})

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ReportChildEditView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ReportChildEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ReportChildEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte Infantil"
        context["pk"] = self.kwargs.get('pk')
        return context

class ReportChildListView(LoginRequiredMixin, ListView):
    model = ReportChild
    template_name = 'core/reportchild_list.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name = "Progenitor").exists():
            parent = Parent.objects.get(user_id = self.request.user.id)
            if parent.is_mother:
                return ReportChild.objects.filter(child__active=True,child__mother = parent, active = True)
            else:
                return ReportChild.objects.filter(child__active=True,child__father = parent, active = True)
        else:
            return ReportChild.objects.filter(child__active=True, active = True)

    def get_context_data(self, **kwargs):
        context = super(ReportChildListView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte Infantil"
        return context
    
class ReportChildListAllView(LoginRequiredMixin, ListView):
    model = ReportChild
    template_name = 'core/reportchild_list.html'

    def get_queryset(self):
        child_id = self.kwargs.get("pk")
        return ReportChild.objects.filter(child_id = child_id)

    def get_context_data(self, **kwargs):
        context = super(ReportChildListAllView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte Infantil"
        return context
    
class ReportChildDeleteView(LoginRequiredMixin, DeleteView):
    model = ReportChild
    def get_success_url(self):
        child_pk = self.object.child.pk 
        return reverse("core:report-all", kwargs={"pk": child_pk})

    def get_context_data(self, **kwargs):
        context = super(ReportChildDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte Infantil"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "El reporte ha sido eliminado.")
        return HttpResponseRedirect(success_url)
    
class ReportChildListHistoryView(LoginRequiredMixin, ListView):
    model = ReportChild
    template_name = 'core/reportchild_history.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name = "Progenitor").exists():
            parent = Parent.objects.get(user_id = self.request.user.id)
            if parent.is_mother:
                return ReportChild.objects.filter(child__active=True,child__mother = parent, active = False)
            else:
                return ReportChild.objects.filter(child__active=True,child__father = parent, active = False)
        else:
            return ReportChild.objects.filter(child__active=True, active = False)

    def get_context_data(self, **kwargs):
        context = super(ReportChildListHistoryView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte Infantil Histórico"
        return context