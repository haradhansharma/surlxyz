
from django.urls import path
from .views import *
from .sitemaps import *
from cms.views import (
    page_detail, 
    blog_detail

)
from selfurl.views import redirect_url
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

app_name = 'main' 

sitemap_list = {
    'static': StaticSitemap,
    'pages' : PageSitemap,
    'category' : CategorySitemap,
    'BlogSitemap' : BlogSitemap,
    'UserBlogSitemap':UserBlogSitemap,
    'BlogArchiveSitemap' : BlogArchiveSitemap,
    'UrlVersionsSitemap' : UrlVersionsSitemap,
    # 'VisiorLogPdfSitemap' : VisiorLogPdfSitemap,
    # 'ClickedPdfSitemap' : ClickedPdfSitemap
}

urlpatterns = [
    path('', index, name='home'),  
    path('b/<str:slug>/', blog_detail, name='blog_details'),    
    path('p/<str:slug>/', page_detail, name='page_detail'), 
    path('webmanifest/', webmanifest, name='webmanifest'),     
    path('sitemap.xml', sitemap, {'sitemaps': sitemap_list}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('<str:short_url>', redirect_url, name='redirect_url'),           
     
    
]












