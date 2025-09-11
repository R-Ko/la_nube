from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.Activity import Activity
from core.models.Child import Child
from core.models.Gallery import Gallery
from core.models.ClassGroup import ClassGroup  # Asegúrate de importar ClassGroup
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
from django.db import transaction  # Importa el módulo de transacciones
from django.core.exceptions import ValidationError  # Importa ValidationError

class GalleryCreateView(LoginRequiredMixin, CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = "core/gallery_form.html"
    
    def get_success_url(self):
        return reverse("core:class-list")
    
    def form_valid(self, form):
        pk = self.kwargs['pk']
        form.instance.classgroup_id = pk
        
        try:
            with transaction.atomic():  # Inicia una transacción atómica
                # Bloquea la fila del ClassGroup para evitar condiciones de carrera
                classgroup = ClassGroup.objects.select_for_update().get(pk=pk)
                
                # Verificar el límite antes de guardar
                current_count = Gallery.objects.filter(classgroup=classgroup).count()
                
                if current_count >= 110:
                    messages.error(self.request, "No se pueden agregar más de 110 fotos/videos a esta galería.")
                    return self.form_invalid(form)
                
                # Guarda el formulario dentro de la transacción
                return super().form_valid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        print('ERROR', form.errors)
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_page"] = "Galería"
        return context