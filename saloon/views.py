from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Salon, Barber, Client
from .forms import SalonForm, BarberForm, ClientForm, SalonSearchForm

class SalonOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        salon = self.get_object()
        return self.request.user == salon.owner

class SalonListView(LoginRequiredMixin, ListView):
    model = Salon
    template_name = 'saloon/salon_list.html'
    context_object_name = 'salons'
    paginate_by = 10

    def get_queryset(self):
        queryset = Salon.objects.filter(owner=self.request.user)
        form = SalonSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            if name:
                queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SalonSearchForm(self.request.GET)
        return context

class SalonCreateView(LoginRequiredMixin, CreateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/salon_form.html'
    success_url = reverse_lazy('saloon:salon_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class SalonUpdateView(SalonOwnerMixin, UpdateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/salon_form.html'
    success_url = reverse_lazy('saloon:salon_list')

class SalonDeleteView(SalonOwnerMixin, DeleteView):
    model = Salon
    template_name = 'saloon/salon_confirm_delete.html'
    success_url = reverse_lazy('saloon:salon_list')

class BarberListView(LoginRequiredMixin, ListView):
    model = Barber
    template_name = 'saloon/barber_list.html'
    context_object_name = 'barbers'
    paginate_by = 10

    def get_queryset(self):
        salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return Barber.objects.filter(salon=salon)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salon'] = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return context

class BarberCreateView(LoginRequiredMixin, CreateView):
    model = Barber
    form_class = BarberForm
    template_name = 'saloon/barber_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

class BarberUpdateView(LoginRequiredMixin, UpdateView):
    model = Barber
    form_class = BarberForm
    template_name = 'saloon/barber_form.html'

    def get_queryset(self):
        return Barber.objects.filter(salon__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

class BarberDeleteView(LoginRequiredMixin, DeleteView):
    model = Barber
    template_name = 'saloon/barber_confirm_delete.html'

    def get_queryset(self):
        return Barber.objects.filter(salon__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'saloon/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return Client.objects.filter(salon=salon)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salon'] = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'saloon/client_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'], owner=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'saloon/client_form.html'

    def get_queryset(self):
        return Client.objects.filter(salon__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'saloon/client_confirm_delete.html'

    def get_queryset(self):
        return Client.objects.filter(salon__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})