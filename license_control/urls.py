
from django.urls import path
from . import views

app_name = 'lc'


urlpatterns = [
    path('key/', views.lc, name='lc'),      
]



