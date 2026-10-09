from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_page, name='dashboard-page'),
    path('api/dashboard/summary/', views.DashboardSummaryAPIView.as_view(), name='api-dashboard-summary'),
]
