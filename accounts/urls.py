from django.urls import path
from .views import (
    BarberSignUpView, ClientSignUpView, CustomLoginView, CustomLogoutView,
    ProfileUpdateView, BarberTypeListView, BarberTypeCreateView,
    BarberListView, BarberCreateView, ClientListView, ClientCreateView,
    UserDeleteView
)

urlpatterns = [
    path('register/barber/', BarberSignUpView.as_view(), name='register_barber'),
    path('register/client/', ClientSignUpView.as_view(), name='register_client'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('barber-types/', BarberTypeListView.as_view(), name='barber_type_list'),
    path('barber-types/create/', BarberTypeCreateView.as_view(), name='barber_type_create'),
    path('barbers/', BarberListView.as_view(), name='barber_list'),
    path('barbers/create/', BarberCreateView.as_view(), name='barber_create'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]
