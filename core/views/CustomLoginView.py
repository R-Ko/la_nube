# core/views/CustomLoginView.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.models import Group

class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.groups.filter(name='Progenitor').exists():
            return reverse_lazy('core:child-list')
        return super().get_success_url()