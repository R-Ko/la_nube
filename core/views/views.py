from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from core.forms import SignUpForm
from core.models.Alert import Alert
from core.models.Family import Family
from core.models.Child import Child
from core.models.Professor import Professor
from core.models.Bill import Bill
from core.models.Parent import Parent
from core.models.User import UserApp
from core.models.PageVisit import PageVisit
from django.contrib.auth.models import User
import datetime
import random
from django.db.models import Sum
import unicodedata

@login_required
def index(request):  
  months = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
  }  
  current_month = months[datetime.date.today().month]
  visits = PageVisit.objects.filter(user__is_staff = False)
  context = {}
  context["family"] = Family.objects.filter(child__active = True).count()
  context["parent"] = Parent.objects.filter(active = True).count()
  context["professor"] = Professor.objects.filter(active = True).count()
  context["childs"] = Child.objects.filter(active = True).count()
  context["bill"] = Bill.objects.filter(month = current_month).count()
  context["amount_bill_usd"] = Bill.objects.filter(month = current_month, currency = "USD").aggregate(Sum("amount"))
  context["amount_bill_euro"] = Bill.objects.filter(month = current_month, currency = "Euro").aggregate(Sum("amount"))
  context["visits"] = visits.count()
  try:
    context["percent_bill"] = context["bill"]/context["childs"]*100
  except:
    context["percent_bill"] = 0
  rol = request.user.groups.all()[0]
  profile = None
  if rol.name == "Progenitor":
    profile = Parent.objects.get(user_id = request.user.id)
  elif rol.name == "Profesor":
    profile = Professor.objects.get(user = request.user)  
    
  if profile != None:    
    null_fields_profile = []
    for field in profile._meta.get_fields():
      if not field.get_internal_type() in ['ForeignKey','BigAutoField']:
        if getattr(profile, field.name) is None:
          null_fields_profile.append(field.verbose_name)
    context["null_fields_profile"] = null_fields_profile  
  
  total_count = 0
  colors = ['primary', 'success', 'danger', 'info', 'warning']
  for item in visits:
    total_count += item.visit_count
  visits_aux = visits.order_by('-visit_count')[:5]
  list_visits = [{'ip': item.ip_address, 'user': item.user, 'count': item.visit_count, 'percen': item.visit_count/total_count*100, 'color': random.choice(colors)} for item in visits_aux]
  context["list_visits"] = list_visits
  template = loader.get_template('base.html')
  return HttpResponse(template.render(context, request))

@login_required
def notify_list(request):    
  alerts = Alert.objects.all().order_by('-publish')
  context = {}
  context["alerts"] = alerts
  template = loader.get_template('core/notify_list.html')
  return HttpResponse(template.render(context, request))


def error_404_view(request, exception):
    return render(request, 'errors/404.html')


def coming_soon(request):
    context = {}
    context['date_end_cooming'] = settings.COMING_SOON_END
    template = loader.get_template('errors/coming_soon.html')
    return HttpResponse(template.render(context, request))

def register(request):
    if request.method == "POST":
        fm = SignUpForm(request.POST)
        if fm.is_valid():
          messages.success(request, 'La cuenta ha sido creada satisfactoriamente.')
          fm.save()
    else:
        fm = SignUpForm()
    return render(request, 'registration/register.html', {'form':fm})
  
@login_required
def terms(request): 
    context = {}
    context['title_page']='Términos y Condiciones'
    template = loader.get_template('core/terms.html')
    if request.user.terms:
      return redirect('core:child-add-one')
    else:
      return HttpResponse(template.render(context, request))
  
@login_required
def set_status_terms(request): 
    user = request.user
    if request.POST['terms_status'] == "accept":
      user.terms = True
      user.save()
    context = {}
    context['user'] = user
    context['title_page'] = 'Términos y Condiciones'
    template = loader.get_template('core/terms.html')
    return redirect('core:child-add-one')
  
@login_required
def create_user_parents(request): 
    parents = Parent.objects.filter(active = True, user = None)
    for parent in parents:
      userapp = UserApp()
      userapp.rol = "Progenitor"
      userapp.nip = parent.nip
      userapp.mother = parent.is_mother
      userapp.terms = False
      userapp.save()      
      user = User.objects.get(pk = userapp.id)
      user.set_password(parent.nip)
      user.first_name = parent.first_name
      user.last_name = parent.last_name
      try:
        first_name = "".join(parent.first_name.split())
        user.username = f"{unicodedata.normalize('NFD', first_name.lower()).encode('ascii', 'ignore').decode('utf-8')}{unicodedata.normalize('NFD', parent.last_name).encode('ascii', 'ignore').decode('utf-8')[:2].lower()}"
      except:
        user.username = f"{unicodedata.normalize('NFD', first_name.lower()).encode('ascii', 'ignore').decode('utf-8')}{unicodedata.normalize('NFD', parent.last_name).encode('ascii', 'ignore').decode('utf-8')[:2].lower()}{parent.nip[:3].lower()}"
      user.save()
    return redirect('core:index')