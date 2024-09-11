from django.urls import path
from . import views

app_name = 'saloonfinance'

urlpatterns = [
    # Cash Register URLs
    path('<int:salon_id>/cashregisters/', views.CashRegisterListView.as_view(), name='cashregister_list'),
    path('<int:salon_id>/cashregisters/create/', views.CashRegisterCreateView.as_view(), name='cashregister_create'),
    path('<int:salon_id>/cashregisters/<int:pk>/update/', views.CashRegisterUpdateView.as_view(), name='cashregister_update'),
    path('<int:salon_id>/cashregisters/<int:pk>/delete/', views.CashRegisterDeleteView.as_view(), name='cashregister_delete'),

    # Payment URLs
    path('<int:salon_id>/payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('<int:salon_id>/payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:salon_id>/payments/<int:pk>/update/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('<int:salon_id>/payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),

    # Transalon URLs
    path('<int:salon_id>/transalons/', views.TransalonListView.as_view(), name='transalon_list'),
    path('<int:salon_id>/transalons/create/', views.TransalonCreateView.as_view(), name='transalon_create'),
    path('<int:salon_id>/transalons/<int:pk>/update/', views.TransalonUpdateView.as_view(), name='transalon_update'),
    path('<int:salon_id>/transalons/<int:pk>/delete/', views.TransalonDeleteView.as_view(), name='transalon_delete'),

    # HTMX field validation URL
    path('validate-field/', views.validate_field, name='validate_field'),
]