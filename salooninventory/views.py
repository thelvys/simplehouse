from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Item, ItemUsed, ItemPurchase
from .forms import (
    ItemForm, ItemUsedForm, ItemPurchaseForm,
    ItemSearchForm, ItemUsedSearchForm, ItemPurchaseSearchForm
)

class HtmxResponseMixin:
    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return HttpResponse(self.get_htmx_response())
        return super().form_valid(form)

    def get_htmx_response(self):
        return ""

class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'salooninventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ItemSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            hairstyle = form.cleaned_data.get('hairstyle')
            salon = form.cleaned_data.get('salon')
            if name:
                queryset = queryset.filter(name__icontains=name)
            if hairstyle:
                queryset = queryset.filter(item_purpose=hairstyle)
            if salon:
                queryset = queryset.filter(salon=salon)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemSearchForm(self.request.GET)
        return context

class ItemCreateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'salooninventory/item_form.html'
    success_url = reverse_lazy('salooninventory:item_list')
    permission_required = 'salooninventory.add_item'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Item created successfully.</div>")

class ItemUpdateView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'salooninventory/item_form.html'
    success_url = reverse_lazy('salooninventory:item_list')
    permission_required = 'salooninventory.change_item'

    def get_htmx_response(self):
        return _("<div class='alert alert-success' role='alert'>Item updated successfully.</div>")

class ItemDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('salooninventory:item_list')
    permission_required = 'salooninventory.delete_item'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse(_("<div class='alert alert-success' role='alert'>Item deleted successfully.</div>"))
        return super().delete(request, *args, **kwargs)

class ItemUsedListView(LoginRequiredMixin, ListView):
    model = ItemUsed
    template_name = 'salooninventory/itemused_list.html'
    context_object_name = 'items_used'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ItemUsedSearchForm(self.request.GET)
        if form.is_valid():
            item = form.cleaned_data.get('item')
            barber = form.cleaned_data.get('barber')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            salon = form.cleaned_data.get('salon')
            if item:
                queryset = queryset.filter(item=item)
            if barber:
                queryset = queryset.filter(barber=barber)
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
            if salon:
                queryset = queryset.filter(salon=salon)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemUsedSearchForm(self.request.GET)

