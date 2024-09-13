from django.urls import path
from . import views

app_name = 'commonapp'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    
    # Currency URLs
    path('currencies/', views.CurrencyListView.as_view(), name='currency_list'),
    path('currencies/create/', views.CurrencyCreateView.as_view(), name='currency_create'),
    path('currencies/<int:pk>/update/', views.CurrencyUpdateView.as_view(), name='currency_update'),
    path('currencies/<int:pk>/delete/', views.CurrencyDeleteView.as_view(), name='currency_delete'),

    # Attachment URLs
    path('attachments/', views.AttachmentListView.as_view(), name='attachment_list'),
    path('attachments/create/', views.AttachmentCreateView.as_view(), name='attachment_create'),
    path('attachments/<int:pk>/update/', views.AttachmentUpdateView.as_view(), name='attachment_update'),
    path('attachments/<int:pk>/delete/', views.AttachmentDeleteView.as_view(), name='attachment_delete'),
]
