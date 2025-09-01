from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, FormView
from core.models.User import UserApp
from django.contrib.auth import get_user_model
from core.forms import UserForm, UserEditForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

UserModel = get_user_model()

class UserCreateView(LoginRequiredMixin, CreateView):
    model = UserApp
    form_class = UserForm
    template_name = 'core/user_form.html'

    def get_success_url(self):
        return reverse("core:user-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(UserCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.nip = self.request.POST["nip"]
        form.instance.created_by = self.request.user
        return super(UserCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Usuarios"
        return context

class UserListView(LoginRequiredMixin, ListView):
    model = UserApp
    template_name = 'core/user_list.html'

    def get_queryset(self):
        return UserModel.objects.exclude(id=self.request.user.id).exclude(is_active=False)

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context["title_page"] = "Usuarios"
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    model = UserApp
    template_name = 'core/user_details.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context["title_page"] = "Usuarios"
        return context

class UserEditView(LoginRequiredMixin, UpdateView):
    model = UserApp
    form_class = UserEditForm
    template_name = 'core/user_form_edit.html'
    success_url = reverse_lazy('core:user-list')
    context_object_name = "usuario"
    
    def form_valid(self, form):
        form.instance.nip = self.request.POST["nip"]
        form.instance.owner = self.request.user
        form.instance.created_by = self.request.user
        return super(UserEditView, self).form_valid(form)

    def form_invalid(self, form):
        print('ERRORS',form.errors)
        return super(UserEditView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Usuarios"
        return context

# class UserDeleteView(LoginRequiredMixin, DeleteView):
#     model = UserApp
#     success_url = reverse_lazy('core:user-list')    
#     template_name = 'core/user_confirm_delete.html'

#     def get_context_data(self, **kwargs):
#         context = super(UserDeleteView, self).get_context_data(**kwargs)
#         context["title_page"] = "User"
#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             p = UserApp.objects.get(pk=int(kwargs['pk']))
#             p.active = False
#             p.save()
#             success_url = self.get_success_url()
#             messages.add_message(request, messages.SUCCESS, "El usuario ha sido eliminado.")
#             return HttpResponseRedirect(success_url)
#         else:
#             return self.form_invalid(form)

#     def form_valid(self, form):
#         success_url = self.get_success_url()
#         return HttpResponseRedirect(success_url)

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = UserApp
    success_url = reverse_lazy('core:user-list')    
    template_name = 'core/user_confirm_delete.html'

    def post(self, request, *args, **kwargs):
        """Ejecuta la eliminación del usuario cuando el formulario se envía"""
        self.object = self.get_object()

        # 🔹 Asegurar que el usuario se elimine de la base de datos
        self.object.delete()

        messages.success(request, "El usuario ha sido eliminado correctamente.")
        return HttpResponseRedirect(self.success_url)
    
class UserListHistoryView(LoginRequiredMixin, ListView):
    model = UserApp
    template_name = 'core/user_history.html'

    def get_queryset(self):
        return UserModel.objects.exclude(id=self.request.user.id).exclude(is_active=True)

    def get_context_data(self, **kwargs):
        context = super(UserListHistoryView, self).get_context_data(**kwargs)
        context["title_page"] = "Usuarios Históricos"
        return context