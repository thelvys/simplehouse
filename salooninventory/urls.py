from django.urls import path
from . import views

app_name = 'salooninventory'

urlpatterns = [
    # Item URLs
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item_update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),

    # ItemUsed URLs
    path('itemsused/', views.ItemUsedListView.as_view(), name='itemused_list'),
    path('itemsused/create/', views.ItemUsedCreateView.as_view(), name='itemused_create'),
    path('itemsused/<int:pk>/update/', views.ItemUsedUpdateView.as_view(), name='itemused_update'),
    path('itemsused/<int:pk>/delete/', views.ItemUsedDeleteView.as_view(), name='itemused_delete'),

    # ItemPurchase URLs
    path('purchases/', views.ItemPurchaseListView.as_view(), name='itempurchase_list'),
    path('purchases/create/', views.ItemPurchaseCreateView.as_view(), name='itempurchase_create'),
    path('purchases/<int:pk>/update/', views.ItemPurchaseUpdateView.as_view(), name='itempurchase_update'),
    path('purchases/<int:pk>/delete/', views.ItemPurchaseDeleteView.as_view(), name='itempurchase_delete'),
]

