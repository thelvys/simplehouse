from django.urls import path
from .views import (
    SalonListView, SalonCreateView, SalonUpdateView, SalonDeleteView,
    SalonAssignmentListView, SalonAssignmentCreateView, SalonAssignmentUpdateView, SalonAssignmentDeleteView
)

urlpatterns = [
    path('salons/', SalonListView.as_view(), name='salon_list'),
    path('salons/create/', SalonCreateView.as_view(), name='salon_create'),
    path('salons/<int:pk>/update/', SalonUpdateView.as_view(), name='salon_update'),
    path('salons/<int:pk>/delete/', SalonDeleteView.as_view(), name='salon_delete'),
    path('assignments/', SalonAssignmentListView.as_view(), name='salon_assignment_list'),
    path('assignments/create/', SalonAssignmentCreateView.as_view(), name='salon_assignment_create'),
    path('assignments/<int:pk>/update/', SalonAssignmentUpdateView.as_view(), name='salon_assignment_update'),
    path('assignments/<int:pk>/delete/', SalonAssignmentDeleteView.as_view(), name='salon_assignment_delete'),
]
