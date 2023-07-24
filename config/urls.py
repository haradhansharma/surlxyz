
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from selfurl.views import redirect_url

admin.site.site_header = 'SELFURL admin'
admin.site.site_title = 'SELFURL admin'
# admin.site.site_url = ''
admin.site.index_title = 'SELFURL administration'
# admin.empty_value_display = '**Empty**'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),  
    path('s/', include('selfurl.urls')),      
    path('accounts/', include('accounts.urls')),     
    path('cms/', include('cms.urls')),  
    path('contact/', include('contact.urls')),             
    path('consent/', include('policy_concent.urls')),     
    path('lc/', include('license_control.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    #Must be at the last
    path('', include('main.urls')),    
    
       
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

