
from django.urls import path
from .views import *



app_name = 'cms'

urlpatterns = [   
    path('latest/blogs/', latest_blogs, name='latest_blogs'),       
    path('category/<str:slug>', category_detail, name='category_detail'),    
    path('archive/<int:year>/<int:month>', archive_detail, name='archive_detail'), 
    path('<str:username>/blogs/', user_blogs, name='user_blogs'), 
  
    
]












