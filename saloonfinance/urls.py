from django.urls import path
from . import views

app_name = 'saloonfinance'

urlpatterns = [
    # Cash Register URLs
    path('cashregisters/', views.CashRegisterListView.as_view(), name='cashregister_list'),
    path('cashregisters/create/', views.CashRegisterCreateView.as_view(), name='cashregister_create'),
    path('cashregisters/<int:pk>/update/', views.CashRegisterUpdateView.as_view(), name='cashregister_update'),
    path('cashregisters/<int:pk>/delete/', views.CashRegisterDeleteView.as_view(), name='cashregister_delete'),

    # Payment URLs
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/update/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),

    # Transalon (Transaction) URLs
    path('transactions/', views.TransalonListView.as_view(), name='transalon_list'),
    path('transactions/create/', views.TransalonCreateView.as_view(), name='transalon_create'),
    path('transactions/<int:pk>/update/', views.TransalonUpdateView.as_view(), name='transalon_update'),
    path('transactions/<int:pk>/delete/', views.TransalonDeleteView.as_view(), name='transalon_delete'),
]
