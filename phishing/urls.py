from django.urls import path
from . import views

urlpatterns = [
    path('', views.display, name='home'),
    path('history/', views.list_history, name='history'),
    path('help/', views.help, name='help'),
    path('store_url/', views.store_url, name='store_url'),
    path('search/', views.search_view, name='search_view'),
    path('csrf_token/', views.csrf_token, name='csrf_token')
]