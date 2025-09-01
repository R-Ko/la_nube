from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.Activity import Activity
from core.models.Child import Child
from core.forms import ActivityForm, ActivityAssignForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader

class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = "core/activity_form.html"

    def get_success_url(self):
        return reverse("core:activity-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ActivityCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ActivityCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActivityCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Actividades Extracurriculares"        
        return context

class ActivityEditView(LoginRequiredMixin, UpdateView):
    model = Activity
    form_class = ActivityForm
    template_name = "core/activity_form.html"

    def get_success_url(self):
        return reverse("core:activity-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ActivityEditView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ActivityEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActivityEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Actividades Extracurriculares"
        return context
    
class ActivityAssignView(LoginRequiredMixin, UpdateView):
    model = Activity
    form_class = ActivityAssignForm
    template_name = "core/activity_form_assign.html"

    def get_success_url(self):
        pk = self.object.pk
        return reverse("core:activity-assign", kwargs={'pk': pk})

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ActivityAssignView, self).form_invalid(form)

    def form_valid(self, form):
        childs_ids = self.request.POST.getlist('childs')
        for id in childs_ids:
            form.instance.childs.add(id)
        form.instance.user = self.request.user
        return super(ActivityAssignView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActivityAssignView, self).get_context_data(**kwargs)
        context["title_page"] = "Actividades Extracurriculares"      
        activity_group = Activity.objects.get(pk=self.kwargs.get('pk'))
        context["childs"] = Child.objects.exclude(activity=activity_group)        
        context["childs_groups"] = Child.objects.filter(activity=activity_group)
        return context

class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'core/activity_list.html'

    def get_queryset(self):
        return Activity.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ActivityListView, self).get_context_data(**kwargs)
        context["title_page"] = "Actividades Extracurriculares"
        return context
    
class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    model = Activity
    success_url = reverse_lazy('core:activity-list')
    template_name = "core/activity_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super(ActivityDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Actividades Extracurriculares"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Activity.objects.get(pk=int(kwargs['pk']))
        p.delete()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "El grupo ha sido eliminado.")
        return HttpResponseRedirect(success_url)
    
@csrf_exempt
@require_http_methods(['POST'])
def delete_child_activity(request):
    child_id = request.POST.get('child_id')    
    activity_id = request.POST.get('activity_id')
    
    activity = Activity.objects.get(
        id = activity_id
    )
    activity.childs.remove(child_id)
    childs_aux = activity.childs.all()
    data = [{'id': child.id, 'name': str(child)} for child in childs_aux]
    return JsonResponse(data, safe=False)

@login_required
def childs_groups(request, pk): 
    context = {}
    classg = Activity.objects.get(id=pk)
    context['classg'] = classg
    context['child_list'] = classg.childs.all()
    template = loader.get_template('core/activity_child_list.html')
    return HttpResponse(template.render(context, request))