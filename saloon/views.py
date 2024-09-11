from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from .models import Salon, Barber, Client, SalonPermission
from .forms import SalonForm, BarberForm, ClientForm, SalonSearchForm, SalonPermissionForm
from config.permissions import SalonOwnerPermissionMixin, CanManageSalonMixin, CanReadSalonMixin

CustomUser = get_user_model()

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class SalonListView(ListView):
    model = Salon
    template_name = 'saloon/salon_list.html'
    context_object_name = 'salons'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SalonSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            address = form.cleaned_data.get('address')
            is_active = form.cleaned_data.get('is_active')
            if name:
                queryset = queryset.filter(name__icontains=name)
            if address:
                queryset = queryset.filter(address__icontains=address)
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SalonSearchForm(self.request.GET, user=self.request.user)
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_list.html']
        return [self.template_name]

class SalonCreateView(HtmxResponseMixin, CreateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/salon_form.html'
    success_url = reverse_lazy('saloon:salon_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, _("Salon created successfully."))
        return super().form_valid(form)

    def get_htmx_response(self):
        return render_to_string('saloon/partials/salon_item.html', {'salon': self.object}, request=self.request)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_form.html']
        return [self.template_name]

class SalonUpdateView(HtmxResponseMixin, SalonOwnerPermissionMixin, UpdateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/salon_form.html'
    success_url = reverse_lazy('saloon:salon_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Salon updated successfully."))
        return super().form_valid(form)

    def get_htmx_response(self):
        return render_to_string('saloon/partials/salon_item.html', {'salon': self.object}, request=self.request)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_form.html']
        return [self.template_name]

class SalonDeleteView(SalonOwnerPermissionMixin, DeleteView):
    model = Salon
    template_name = 'saloon/salon_confirm_delete.html'
    success_url = reverse_lazy('saloon:salon_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, _("Salon deleted successfully."))
        if request.htmx:
            return HttpResponse(status=204)
        return HttpResponseRedirect(success_url)

class BarberListView(CanReadSalonMixin, ListView):
    model = Barber
    template_name = 'saloon/barber_list.html'
    context_object_name = 'barbers'
    paginate_by = 10

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Barber.objects.filter(salon_id=salon_id)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/barber_list.html']
        return [self.template_name]

class BarberCreateView(HtmxResponseMixin, CanManageSalonMixin, CreateView):
    model = Barber
    form_class = BarberForm
    template_name = 'saloon/barber_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = get_object_or_404(Salon, pk=self.kwargs['salon_id'])
        return kwargs

    def form_valid(self, form):
        form.instance.salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'])
        messages.success(self.request, _("Barber created successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

    def get_htmx_response(self):
        return render_to_string('saloon/partials/barber_item.html', {'barber': self.object}, request=self.request)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/barber_form.html']
        return [self.template_name]

class BarberUpdateView(HtmxResponseMixin, CanManageSalonMixin, UpdateView):
    model = Barber
    form_class = BarberForm
    template_name = 'saloon/barber_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = self.object.salon
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Barber updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

    def get_htmx_response(self):
        return render_to_string('saloon/partials/barber_item.html', {'barber': self.object}, request=self.request)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/barber_form.html']
        return [self.template_name]

class BarberDeleteView(CanManageSalonMixin, DeleteView):
    model = Barber
    template_name = 'saloon/barber_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, _("Barber deleted successfully."))
        if request.htmx:
            return HttpResponse(status=204)
        return HttpResponseRedirect(success_url)

class ClientListView(CanReadSalonMixin, ListView):
    model = Client
    template_name = 'saloon/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Client.objects.filter(salon_id=salon_id)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/client_list.html']
        return [self.template_name]

class ClientCreateView(HtmxResponseMixin, CanManageSalonMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'saloon/client_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = get_object_or_404(Salon, pk=self.kwargs['salon_id'])
        return kwargs

    def form_valid(self, form):
        form.instance.salon = get_object_or_404(Salon, pk=self.kwargs['salon_id'])
        messages.success(self.request, _("Client created successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

    def get_htmx_response(self):
        return render_to_string('saloon/partials/client_item.html', {'client': self.object}, request=self.request)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/client_form.html']
        return [self.template_name]

class ClientUpdateView(HtmxResponseMixin, CanManageSalonMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'saloon/client_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = self.object.salon
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Client updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

    def get_htmx_response(self):
        return render_to_string('saloon/partials/client_item.html', {'client': self.object}, request=self.request)

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/client_form.html']
        return [self.template_name]

class ClientDeleteView(CanManageSalonMixin, DeleteView):
    model = Client
    template_name = 'saloon/client_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, _("Client deleted successfully."))
        if request.htmx:
            return HttpResponse(status=204)
        return HttpResponseRedirect(success_url)

class ManageSalonPermissionsView(SalonOwnerPermissionMixin, FormView):
    template_name = 'saloon/manage_permissions.html'
    form_class = SalonPermissionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['salon'] = get_object_or_404(Salon, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        salon = get_object_or_404(Salon, pk=self.kwargs['pk'])
        context['salon'] = salon
        context['permissions'] = SalonPermission.objects.filter(salon=salon)
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, pk=self.kwargs['pk'])
        user = form.cleaned_data['user']
        permission_type = form.cleaned_data['permission_type']
        
        if form.cleaned_data['action'] == 'add':
            SalonPermission.objects.get_or_create(salon=salon, user=user, permission_type=permission_type)
            messages.success(self.request, _("Permission added successfully."))
        elif form.cleaned_data['action'] == 'remove':
            SalonPermission.objects.filter(salon=salon, user=user, permission_type=permission_type).delete()
            messages.success(self.request, _("Permission removed successfully."))
        
        if self.request.htmx:
            context = self.get_context_data()
            return render(self.request, 'saloon/partials/permission_list.html', context)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:manage_permissions', kwargs={'pk': self.kwargs['pk']})
