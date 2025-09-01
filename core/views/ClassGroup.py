from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from core.models.ClassGroup import ClassGroup
from core.models.Child import Child
from core.models.Gallery import Gallery
from core.forms import ClassGroupForm, ClassGroupAssignForm
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

class ClassGroupCreateView(LoginRequiredMixin, CreateView):
    model = ClassGroup
    form_class = ClassGroupForm
    template_name = "core/class_form.html"

    def get_success_url(self):
        return reverse("core:class-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ClassGroupCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ClassGroupCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ClassGroupCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Grupos"        
        return context

class ClassGroupEditView(LoginRequiredMixin, UpdateView):
    model = ClassGroup
    form_class = ClassGroupForm
    template_name = "core/class_form.html"

    def get_success_url(self):
        return reverse("core:class-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ClassGroupEditView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ClassGroupEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ClassGroupEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Grupos"
        return context
    
class ClassGroupAssignView(LoginRequiredMixin, UpdateView):
    model = ClassGroup
    form_class = ClassGroupAssignForm
    template_name = "core/class_form_assign.html"

    def get_success_url(self):
        pk = self.object.pk
        return reverse("core:class-assign", kwargs={'pk': pk})

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(ClassGroupAssignView, self).form_invalid(form)

    def form_valid(self, form):
        childs_ids = self.request.POST.getlist('childs')
        for id in childs_ids:
            form.instance.childs.add(id)
        form.instance.user = self.request.user
        return super(ClassGroupAssignView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ClassGroupAssignView, self).get_context_data(**kwargs)
        context["title_page"] = "Grupos"      
        class_group = ClassGroup.objects.get(pk=self.kwargs.get('pk'))
        context["childs"] = Child.objects.exclude(classgroup=class_group)        
        context["childs_groups"] = Child.objects.filter(classgroup=class_group)
        return context

class ClassGroupListView(LoginRequiredMixin, ListView):
    model = ClassGroup
    template_name = 'core/class_list.html'

    def get_queryset(self):
        return ClassGroup.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ClassGroupListView, self).get_context_data(**kwargs)
        context["title_page"] = "Grupos"
        return context
    
class ClassGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = ClassGroup
    success_url = reverse_lazy('core:class-list')
    template_name = "core/class_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super(ClassGroupDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Grupos"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = ClassGroup.objects.get(pk=int(kwargs['pk']))
        p.delete()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "El grupo ha sido eliminado.")
        return HttpResponseRedirect(success_url)
    
@csrf_exempt
@require_http_methods(['POST'])
def delete_child_group(request):
    child_id = request.POST.get('child_id')    
    class_id = request.POST.get('class_id')
    
    classgroup = ClassGroup.objects.get(
        id = class_id
    )
    classgroup.childs.remove(child_id)
    childs_aux = classgroup.childs.all()
    data = [{'id': child.id, 'name': str(child)} for child in childs_aux]
    return JsonResponse(data, safe=False)

class ClassChildListView(LoginRequiredMixin, UpdateView):
    model = ClassGroup
    template_name = 'core/class_child_list.html'

    def get_queryset(self):
        pk = self.kwargs['pk']
        classg = ClassGroup.objects.get(id=pk)
        queryset = classg.childs.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClassChildListView, self).get_context_data(**kwargs)
        return context
    
@login_required
def childs_groups(request, pk): 
    context = {}
    classg = ClassGroup.objects.get(id=pk)
    context['classg'] = classg
    context['child_list'] = classg.childs.all()
    template = loader.get_template('core/class_child_list.html')
    return HttpResponse(template.render(context, request))

@login_required
def gallery_class(request, pk): 
    context = {}
    classg = ClassGroup.objects.get(id=pk)
    gallery = Gallery.objects.filter(classgroup = classg)
    template = loader.get_template('core/gallery.html')
    context['classg'] = classg
    context['gallery'] = gallery
    return HttpResponse(template.render(context, request))