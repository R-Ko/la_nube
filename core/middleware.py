from django.shortcuts import reverse, redirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from core.models.PageVisit import PageVisit
from django.contrib.auth.models import AnonymousUser
class ComingSoonModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get('PATH_INFO', "")

        if settings.COMING_SOON_MODE and path!= reverse("coming-soon"):
            response = redirect(reverse("coming-soon"))
            return response

        response = self.get_response(request)

        return response

class CountVisitsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip admin or static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return
        if "HTTP_X_FORWARDED_FOR" in request.META:
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]
        ip_address = request.META.get('REMOTE_ADDR')
        if str(request.user) != 'AnonymousUser':
            page, created = PageVisit.objects.get_or_create(user=request.user)
            page.visit_count += 1
            page.ip_address = ip_address or None
            page.save()


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"\n=== Middleware Debug ===")
        print(f"Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
        if request.user.is_authenticated:
            print(f"ID de usuario: {request.user.id}")
            print(f"must_change_password: {getattr(request.user, 'must_change_password', 'NO EXISTE')}")
            print(f"Tipo de usuario: {type(request.user)}")
            
            # Forzar recarga desde la base de datos
            from core.models.User import UserApp
            try:
                user_db = UserApp.objects.get(id=request.user.id)
                print(f"Valor en BD: {user_db.must_change_password}")
            except Exception as e:
                print(f"Error al consultar BD: {e}")
        
        print(f"Path: {request.path}")
        print("=======================\n")
        
        if request.user.is_authenticated:
            if getattr(request.user, "must_change_password", False):
                allowed_urls = [
                    reverse("cambiar_password"),
                    reverse("logout"),
                ]
                if request.path not in allowed_urls:
                    return redirect("cambiar_password")
        
        return self.get_response(request)