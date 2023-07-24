
from django.urls import path
from .views import *
from django.views.generic.base import TemplateView



app_name = 'selfurl'



urlpatterns = [ 
    path('report-malicious/', report_malicious, name='report_malicious'),
    path('statistics/', statistics, name='statistics'),   
    path('makeshort/', makeshort, name='makeshort'),   
    path('versions/<str:short_url>', versions, name='versions'),   
    path('create-version/<str:short_url>', create_version, name='create_version'),  
    path('logs/<str:short_url>/', log_details, name='log_details'), 
    path('set-expire/<int:id>/', set_expire, name='set_expire'), 
    path('malicious-submit/', malicious_submit, name='malicious_submit'), 
    path('allreport/<str:short_url>', allreport, name='allreport'),
    path('report-pdf/<str:short_url>', generate_visitor_log_pdf, name='generate_visitor_log_pdf'),
    path('click-record-pdf/<str:short_url>', generate_click_record_pdf_view, name='generate_click_record_pdf_view'),
    
    
] 


