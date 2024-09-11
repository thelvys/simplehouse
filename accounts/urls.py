from django.urls import path
from .views import (
    SignUpView, CustomLoginView, CustomLogoutView,
    ProfileUpdateView, UserListView, UserDeleteView,
    validate_field
)

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('validate-field/', validate_field, name='validate_field'),
    
    # HTMX specific paths
    path('users/search/', UserListView.as_view(), name='user_search'),
]
