from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models.Bill import Bill
from core.models.Parent import Parent
from core.models.Child import Child
from core.forms import BillForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

class BillCreateView(LoginRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = "core/bill_form.html"

    def get_success_url(self):
        return reverse("core:bill-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(BillCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BillCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BillCreateView, self).get_context_data(**kwargs)
        context["title_page"] = "Facturas"        
        context["childs"] = Child.objects.filter(active=True)
        return context

class BillEditView(LoginRequiredMixin, UpdateView):
    model = Bill
    form_class = BillForm
    template_name = "core/bill_form.html"

    def get_success_url(self):
        return reverse("core:bill-list")

    def form_invalid(self, form):
        print('ERROR',form.errors)
        return super(BillEditView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BillEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BillEditView, self).get_context_data(**kwargs)
        context["title_page"] = "Facturas"        
        context["childs"] = Child.objects.filter(active=True)
        return context

class BillListView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'core/bill_list.html'

    def get_queryset(self):
        return Bill.objects.filter(active = True)

    def get_context_data(self, **kwargs):
        context = super(BillListView, self).get_context_data(**kwargs)
        context["title_page"] = "Facturas"
        return context
    
class BillDeleteView(LoginRequiredMixin, DeleteView):
    model = Bill
    success_url = reverse_lazy('core:bill-list')

    def get_context_data(self, **kwargs):
        context = super(BillDeleteView, self).get_context_data(**kwargs)
        context["title_page"] = "Facturas"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p = Bill.objects.get(pk=int(kwargs['pk']))
        p.active = False
        p.save()
        success_url = self.get_success_url()
        messages.add_message(request, messages.SUCCESS, "La factura ha sido eliminada.")
        return HttpResponseRedirect(success_url)
    
class BillListHistoryView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'core/bill_history.html'

    def get_queryset(self):
        return Bill.objects.filter(active = False)

    def get_context_data(self, **kwargs):
        context = super(BillListHistoryView, self).get_context_data(**kwargs)
        context["title_page"] = "Facturas Históricas"
        return context
    
@csrf_exempt
@require_http_methods(['GET'])
def get_data(request):
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
    bills = Bill.objects.filter(month = current_month).count()
    childs = Child.objects.filter(active = True).count()
    
    bills_anterior = Bill.objects.filter(month = months[datetime.date.today().month-1]).count()
    bills_proximo = Bill.objects.filter(month = months[datetime.date.today().month+1]).count()
    
    usd = Bill.objects.filter(month = current_month, currency = 'USD').count()
    mlc = Bill.objects.filter(month = current_month, currency = 'MLC').count()
    usa = Bill.objects.filter(month = current_month, currency = 'USA Zelle').count()
    euro = Bill.objects.filter(month = current_month, currency = 'Euro').count()
    data = {'bills': bills, 'childs': childs, 'usd': usd, 'mlc': mlc, 'usa': usa, 'euro': euro, 'bills_anterior': bills_anterior, 'bills_proximo': bills_proximo}
    return JsonResponse(data, safe=False)