from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.AssistanceDaily import AssistanceDaily
from core.forms import AssistanceDailyForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin

class AssistanceDailyProfessorListView(LoginRequiredMixin, ListView):
    model = AssistanceDaily
    template_name = 'core/assistance_daily_list.html'
    context_object_name = 'assistances_list'
    
    def get_queryset(self):
        return AssistanceDaily.objects.filter(child = None)

    def get_context_data(self, **kwargs):
        context = super(AssistanceDailyProfessorListView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte de Asistencia (Educadoras)"
        return context
    
class AssistanceDailyChildListView(LoginRequiredMixin, ListView):
    model = AssistanceDaily
    template_name = 'core/assistance_daily_list.html'
    context_object_name = 'assistances_list'
    
    def get_queryset(self):
        return AssistanceDaily.objects.filter(professor = None)

    def get_context_data(self, **kwargs):
        context = super(AssistanceDailyChildListView, self).get_context_data(**kwargs)
        context["title_page"] = "Reporte de Asistencia (Niños)"
        return context



class AssistanceDailyCreateView(CreateView):
    model = AssistanceDaily
    form_class = AssistanceDailyForm
    template_name = 'assistance_daily_form.html'
    success_url = reverse_lazy('assistance_daily_list')

class AssistanceDailyUpdateView(UpdateView):
    model = AssistanceDaily
    form_class = AssistanceDailyForm
    template_name = 'assistance_daily_form.html'
    success_url = reverse_lazy('assistance_daily_list')

class AssistanceDailyDeleteView(DeleteView):
    model = AssistanceDaily
    template_name = 'assistance_daily_confirm_delete.html'
    success_url = reverse_lazy('assistance_daily_list')
    
    
@csrf_exempt
@require_http_methods(['POST'])
def save_daily_child(request):
    child = request.POST.get('child')
    
    assistance_obj = AssistanceDaily()
    assistance_obj.date = datetime.now()
    assistance_obj.created_by = request.user
    assistance_obj.child_id = child
    assistance_obj.save()
    
    return JsonResponse({'message': 'Saved successfully'})


@csrf_exempt
@require_http_methods(['POST'])
def save_daily_professor(request):
    professor = request.POST.get('professor')
    
    assistance_obj = AssistanceDaily()
    assistance_obj.date = datetime.now()
    assistance_obj.created_by = request.user
    assistance_obj.professor_id = professor
    assistance_obj.save()
    
    return JsonResponse({'message': 'Saved successfully'})