from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('<user_id>', views.thatperson, name='thatperson'),
    path('search/', views.search, name='search'),
]
