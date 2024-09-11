from django.urls import path
from . import views

app_name = 'salooninventory'

urlpatterns = [
    # Item URLs
    path('<int:salon_id>/items/', views.ItemListView.as_view(), name='item_list'),
    path('<int:salon_id>/items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('<int:salon_id>/items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item_update'),
    path('<int:salon_id>/items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),

    # ItemUsed URLs
    path('<int:salon_id>/items-used/', views.ItemUsedListView.as_view(), name='itemused_list'),
    path('<int:salon_id>/items-used/create/', views.ItemUsedCreateView.as_view(), name='itemused_create'),

    # ItemPurchase URLs
    path('<int:salon_id>/purchases/', views.ItemPurchaseListView.as_view(), name='itempurchase_list'),
    path('<int:salon_id>/purchases/create/', views.ItemPurchaseCreateView.as_view(), name='itempurchase_create'),

    # HTMX specific URLs
    path('validate-field/', views.validate_field, name='validate_field'),
]