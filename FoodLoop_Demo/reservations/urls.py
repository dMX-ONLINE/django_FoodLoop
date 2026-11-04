from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('review/<int:pk>/', views.review, name='review'),
    path('reservation/<int:pk>/',views.reservation,name='reservation'),
    path('manage_reservations/',views.manage_reservations,name='manage_reservations'),
    path('reservation_action/<int:pk>/',views.reservation_action,name='reservation_action'),
    path('view_image/<int:pk>/', views.view_image, name='view_image'),
]