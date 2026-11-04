from django.urls import path
from .views import index
from .views import about
from .views import welcome

app_name = "core"

urlpatterns = [
    path('', welcome, name='welcome'),
    path('/home', index, name='index'),
    path('/aboout', about, name='about'),
]