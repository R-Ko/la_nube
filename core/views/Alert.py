from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from core.models.Alert import Alert
from core.models.Parent import Parent
from core.forms import AlertForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime

class AlertCreateView(LoginRequiredMixin, CreateView):
    model = Alert
    form_class = AlertForm
    template_name = "core/alert_form.html"

    def get_success_url(self):
        return reverse("core:alert-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(AlertCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AlertCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AlertCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Alertas"        
        return context

class AlertEditView(LoginRequiredMixin, UpdateView):
    model = Alert
    form_class = AlertForm
    template_name = "core/alert_form.html"

    def get_success_url(self):
        return reverse("core:alert-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(AlertEditView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AlertEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AlertEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Alertas"
        return context

class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = 'core/alert_list.html'

    def get_queryset(self):
        return Alert.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AlertListView, self).get_context_data(**kwargs)
        context["title_page"] = "Alertas"
        return context
    
class AlertDeleteView(LoginRequiredMixin, DeleteView):
    model = Alert
    success_url = reverse_lazy('core:alert-list')

    def get_context_data(self, **kwargs):
        context = super(AlertDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Alertas"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Alert.objects.get(pk=int(kwargs['pk']))
        p.delete()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "La alerta ha sido eliminada.")
        return HttpResponseRedirect(success_url)
    
@csrf_exempt
@require_http_methods(['POST'])
def get_alerts(request):
    now = datetime.datetime.now()
    date_aux = now - datetime.timedelta(days=30)
    alerts = Alert.objects.filter(active = True, publish__lte = now).exclude(publish__lte = date_aux).order_by('-publish')[:4]
    data = [{'title': alert.title, 'content': alert.content, 'publish': alert.publish.strftime("%d-%m-%Y")} for alert in alerts]
    return JsonResponse(data, safe=False)