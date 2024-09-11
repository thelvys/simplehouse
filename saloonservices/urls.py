from django.urls import path
from . import views

app_name = 'saloonservices'

urlpatterns = [
    # Hairstyle URLs
    path('<int:salon_id>/hairstyles/', views.HairstyleListView.as_view(), name='hairstyle_list'),
    path('<int:salon_id>/hairstyles/create/', views.HairstyleCreateView.as_view(), name='hairstyle_create'),
    path('<int:salon_id>/hairstyles/<int:pk>/update/', views.HairstyleUpdateView.as_view(), name='hairstyle_update'),
    path('<int:salon_id>/hairstyles/<int:pk>/delete/', views.HairstyleDeleteView.as_view(), name='hairstyle_delete'),

    # Shave URLs
    path('<int:salon_id>/shaves/', views.ShaveListView.as_view(), name='shave_list'),
    path('<int:salon_id>/shaves/create/', views.ShaveCreateView.as_view(), name='shave_create'),
    path('<int:salon_id>/shaves/<int:pk>/update/', views.ShaveUpdateView.as_view(), name='shave_update'),
    path('<int:salon_id>/shaves/<int:pk>/delete/', views.ShaveDeleteView.as_view(), name='shave_delete'),

    # HairstyleTariffHistory URLs
    path('<int:salon_id>/tariff-history/', views.HairstyleTariffHistoryListView.as_view(), name='hairstyletariffhistory_list'),
    path('<int:salon_id>/tariff-history/create/', views.HairstyleTariffHistoryCreateView.as_view(), name='hairstyletariffhistory_create'),

    # HTMX specific URLs
    path('validate-field/', views.validate_field, name='validate_field'),
]
