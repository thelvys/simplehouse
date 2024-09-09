from django.urls import path
from . import views

app_name = 'saloonservices'

urlpatterns = [
    # Hairstyle URLs
    path('hairstyles/', views.HairstyleListView.as_view(), name='hairstyle_list'),
    path('hairstyles/create/', views.HairstyleCreateView.as_view(), name='hairstyle_create'),
    path('hairstyles/<int:pk>/update/', views.HairstyleUpdateView.as_view(), name='hairstyle_update'),
    path('hairstyles/<int:pk>/delete/', views.HairstyleDeleteView.as_view(), name='hairstyle_delete'),

    # Shave URLs
    path('shaves/', views.ShaveListView.as_view(), name='shave_list'),
    path('shaves/create/', views.ShaveCreateView.as_view(), name='shave_create'),
    path('shaves/<int:pk>/update/', views.ShaveUpdateView.as_view(), name='shave_update'),
    path('shaves/<int:pk>/delete/', views.ShaveDeleteView.as_view(), name='shave_delete'),

    # HairstyleTariffHistory URLs
    path('tariffhistory/', views.HairstyleTariffHistoryListView.as_view(), name='hairstyletariffhistory_list'),
    path('tariffhistory/create/', views.HairstyleTariffHistoryCreateView.as_view(), name='hairstyletariffhistory_create'),
    path('tariffhistory/<int:pk>/update/', views.HairstyleTariffHistoryUpdateView.as_view(), name='hairstyletariffhistory_update'),
    path('tariffhistory/<int:pk>/delete/', views.HairstyleTariffHistoryDeleteView.as_view(), name='hairstyletariffhistory_delete'),
]
