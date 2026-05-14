from django.urls import path
from . import views

urlpatterns = [
    path('api/analyze/', views.analyze_product, name='analyze_product'),
]
