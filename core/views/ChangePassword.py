from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from core.forms import CustomPasswordChangeForm,PasswordResetForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from core.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

UserModel = get_user_model()

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.must_change_password = False  # Importante: desactivar el flag
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Contraseña actualizada correctamente!')
            return redirect('/')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    # Pasar la variable force_change al template
    return render(request, 'registration/cambiar_password.html', {
        'form': form,
        'force_change': request.user.must_change_password  # <-- Esto es clave
    })

def reset_password(request):
    if request.method != 'POST':
        return render(request, 'registration/reset_password.html', {'form': PasswordResetForm()})
    form = PasswordResetForm(request.POST)
    response = render(request, 'registration/reset_password.html', {'form': form})
    if not form.is_valid():
        return response
    try:
        user = UserModel.objects.get(username=form.cleaned_data['username'])
    except UserModel.DoesNotExist:
        messages.error(request, 'usuario no encontrado')
        return response
    if not user.security_answer or not user.security_question:
        messages.error(request, 'usuario no tiene pregunta o respuesta de seguridad')
        return response
    form_security_question = form.cleaned_data['security_question']
    form_security_answer = form.cleaned_data['security_answer']
    if not form_security_question or not form_security_answer:
        messages.error(request, 'debe mandar pregunta y respuesta de seguridad')
        return response
    same_question = user.security_question == form_security_question
    same_answer = user.security_answer == form_security_answer
    if not (same_question and same_answer):
        messages.error(request, 'pregunta o respuesta de seguridad no valida')
        return response
    passwd1,passwd2  = form.cleaned_data['new_password1'],form.cleaned_data['new_password2']
    if  passwd1 != passwd2:
        messages.error(request, 'los dos password no coinciden')
        return response
    try:
        validate_password(passwd1)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return response
    user.password = make_password(passwd1)
    user.must_change_password = False
    user.save()  
    user.save()  
    messages.success(request, 'Your password was successfully updated!')
    return redirect('/')


@csrf_exempt
def get_security_question(request):
    username = request.GET.get("username")
    if not username:
        return JsonResponse({"error": "username requerido"}, status=400)

    try:
        user = UserModel.objects.get(username=username)
        if user.security_question:
            return JsonResponse({"question": user.security_question})
        else:
            return JsonResponse({"error": "usuario sin pregunta"}, status=404)
    except UserModel.DoesNotExist:
        return JsonResponse({"error": "usuario no encontrado"}, status=404)
