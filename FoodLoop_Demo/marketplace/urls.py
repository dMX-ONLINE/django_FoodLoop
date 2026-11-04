from django.urls import path
from .views import marketplace
from .views import offerfood
from .views import viewfood


app_name = 'marketplace'


urlpatterns = [
    path('', marketplace, name='marketplace'),
    path('offerfood/', offerfood, name='offerfood'),
    path('viewfood/<int:pk>/', viewfood, name='viewfood'),
]