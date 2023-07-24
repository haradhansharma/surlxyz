
from django.urls import path, include
from .views import *




app_name = 'policy_concent'



urlpatterns = [
    path('set_concent/', set_concent, name='set_concent'),    
]
