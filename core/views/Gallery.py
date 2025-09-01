from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.Activity import Activity
from core.models.Child import Child
from core.models.Gallery import Gallery
from core.forms import GalleryForm
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
from datetime import datetime
class GalleryCreateView(LoginRequiredMixin, CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = "core/gallery_form.html"

    def get_success_url(self):
        return reverse("core:class-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(GalleryCreateView, self).form_invalid(form)

    def form_valid(self, form):
        pk = self.kwargs['pk']
        # date = datetime.now().date()
        # if Gallery.objects.filter(classgroup_id = pk, date = date).exists():
        #     obj = Gallery.objects.get(classgroup_id = pk, date = date)
        #     obj.image = form.instance.image
        #     obj.save()
        #     return HttpResponseRedirect(self.get_success_url())        
        form.instance.classgroup_id = pk
        return super(GalleryCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(GalleryCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Galería"        
        return context
