from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.Event import Event
from core.forms import EventForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "core/event_form.html"

    def get_success_url(self):
        return reverse("core:event-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(EventCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EventCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Eventos"
        return context

class EventEditView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "core/event_form.html"

    def get_success_url(self):
        return reverse("core:event-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(EventEditView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EventEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Eventos"
        return context

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'core/event_list.html'

    def get_queryset(self):
        return Event.objects.all()

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context["title_page"] = "Eventos"
        return context
    
class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('core:event-list')

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Eventos"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Event.objects.get(pk=int(kwargs['pk']))
        p.delete()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "El evento ha sido eliminado.")
        return HttpResponseRedirect(success_url)

class CalendarListView(LoginRequiredMixin,ListView):
    model = Event
    template_name = 'core/calendar.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarListView, self).get_context_data(**kwargs)
        context["title_page"] = "Calendario de Eventos"
        return context

@login_required   
def get_events(request):
    events = Event.objects.all()
    result = []
    for event in events:
        json = {}
        json["title"] = event.name
        start = datetime.datetime(day=event.date.day,month=event.date.month,year=event.date.year)
        json["start"] = (int)(start.timestamp() * 1000)
        json["end"] = (int)(start.timestamp() * 1000)
        json["rendering"] = 'background'
        json["constraint"] = 'businessHours'
        result.append(json)
    return JsonResponse(result, safe=False)