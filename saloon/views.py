from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Salon, SalonAssignment
from .forms import SalonForm, SalonAssignmentForm, SalonSearchForm, SalonAssignmentSearchForm

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
        form = SalonSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            is_active = form.cleaned_data.get('is_active')
            if search:
                queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
            if is_active:
                queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SalonSearchForm(self.request.GET)
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_list.html']
        return [self.template_name]

class SalonCreateView(HtmxResponseMixin, CreateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/salon_create.html'
    success_url = reverse_lazy('salon_list')

    def get_htmx_response(self):
        return f'<tr><td>{self.object.name}</td><td>{self.object.owner}</td><td>{self.object.is_active}</td></tr>'

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_form.html']
        return [self.template_name]

class SalonUpdateView(HtmxResponseMixin, UpdateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/salon_update.html'
    success_url = reverse_lazy('salon_list')

    def get_htmx_response(self):
        return f'<tr><td>{self.object.name}</td><td>{self.object.owner}</td><td>{self.object.is_active}</td></tr>'

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_form.html']
        return [self.template_name]

class SalonDeleteView(DeleteView):
    model = Salon
    success_url = reverse_lazy('salon_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(status=204)
        return super().delete(request, *args, **kwargs)

class SalonAssignmentListView(ListView):
    model = SalonAssignment
    template_name = 'saloon/salon_assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SalonAssignmentSearchForm(self.request.GET)
        if form.is_valid():
            salon = form.cleaned_data.get('salon')
            barber = form.cleaned_data.get('barber')
            is_active = form.cleaned_data.get('is_active')
            date = form.cleaned_data.get('date')
            if salon:
                queryset = queryset.filter(salon=salon)
            if barber:
                queryset = queryset.filter(Q(barber__first_name__icontains=barber) | Q(barber__last_name__icontains=barber))
            if is_active:
                queryset = queryset.filter(is_active=True)
            if date:
                queryset = queryset.filter(start_date__lte=date, end_date__gte=date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SalonAssignmentSearchForm(self.request.GET)
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_assignment_list.html']
        return [self.template_name]

class SalonAssignmentCreateView(HtmxResponseMixin, CreateView):
    model = SalonAssignment
    form_class = SalonAssignmentForm
    template_name = 'saloon/salon_assignment_create.html'
    success_url = reverse_lazy('salon_assignment_list')

    def get_htmx_response(self):
        return f'<tr><td>{self.object.salon}</td><td>{self.object.barber}</td><td>{self.object.start_date}</td><td>{self.object.end_date}</td><td>{self.object.is_active}</td></tr>'

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_assignment_form.html']
        return [self.template_name]

class SalonAssignmentUpdateView(HtmxResponseMixin, UpdateView):
    model = SalonAssignment
    form_class = SalonAssignmentForm
    template_name = 'saloon/salon_assignment_update.html'
    success_url = reverse_lazy('salon_assignment_list')

    def get_htmx_response(self):
        return f'<tr><td>{self.object.salon}</td><td>{self.object.barber}</td><td>{self.object.start_date}</td><td>{self.object.end_date}</td><td>{self.object.is_active}</td></tr>'

    def get_template_names(self):
        if self.request.htmx:
            return ['saloon/partials/salon_assignment_form.html']
        return [self.template_name]

class SalonAssignmentDeleteView(DeleteView):
    model = SalonAssignment
    success_url = reverse_lazy('salon_assignment_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(status=204)
        return super().delete(request, *args, **kwargs)
