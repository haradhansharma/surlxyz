
from django.urls import path
from . views import *



app_name = 'contact'

urlpatterns = [
    path('', contact, name='contact'),
    path('threads/<str:email>', threads, name='threads'), 
    path('threads-reply-form/<int:id>', get_reply_form, name='get_reply_form'), 
    path('post-reply/<int:id>', post_reply, name='post_reply'),    
       
       
        
    
]












