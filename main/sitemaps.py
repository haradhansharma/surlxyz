from django.contrib import sitemaps
from django.urls import reverse

from accounts.models import User
from main.helper import get_blog_archive, get_blogs, pages
from selfurl.models import Shortener
from .models import *
from cms.models import *
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
 

class StaticSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            'main:home', 
            'contact:contact', 
            'cms:latest_blogs',
            'accounts:signup',
            'accounts:login',  
            'selfurl:report_malicious',
            'selfurl:statistics'       
            
            ] 
    
    def lastmod(self, obj):
        return timezone.now()
        
    def location(self, item):
        return reverse(item)   
    
class PageSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9    

    def items(self):
        return pages()[:10]
    
    def lastmod(self, obj):
        return obj.created_at
        
    def location(self, obj):
        return obj.get_absolute_url()
    
class CategorySitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 1    

    def items(self):
        categories_with_blogs = Category.objects.filter(
            is_active=True
        ).annotate(
            blog_count=Count('blogs_category')
        ).filter(
            blog_count__gt=0
        )
        categories = [category for category in categories_with_blogs if category.blog_count > 0]
        return categories
    
    def lastmod(self, obj):
        return obj.created_at
        
    def location(self, obj):
        return obj.get_absolute_url()
    
class BlogSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 1.0    

    def items(self):
        blogs = get_blogs()[:20]
        return blogs
    
    def lastmod(self, obj):
        return obj.created_at
        
    def location(self, obj):
        return obj.get_absolute_url()
    
class UserBlogSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9    

    def items(self):
        users = User.objects.filter(is_active = True).order_by('-date_joined')[:20]
        return users
    
    def lastmod(self, obj):
        return obj.date_joined
        
    def location(self, obj):
        return reverse('cms:user_blogs', args=[str(obj.username)])
    
class BlogArchiveSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9    

    def items(self):
        archives = get_blog_archive()[:50]
        print(archives)
        return archives
    
    def lastmod(self, obj):
        return obj.get('month')
        
    def location(self, obj):
        return reverse('cms:archive_detail', args=[str(obj.get('month').strftime('%Y')), str(obj.get('month').strftime('%m'))])
    
class UrlVersionsSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9    

    def items(self):
        versions = Shortener.objects.filter(active=True)[:20]
        return versions
    
    def lastmod(self, obj):
        return obj.created
        
    def location(self, obj):
        return reverse('selfurl:versions', args=[str(obj.short_url)])
    
class VisiorLogPdfSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9    

    def items(self):
        versions = Shortener.objects.exclude(creator = None).filter(active=True)[:20]
        return versions
    
    def lastmod(self, obj):
        return obj.created
        
    def location(self, obj):
        return reverse('selfurl:generate_visitor_log_pdf', args=[str(obj.short_url)])
    
class ClickedPdfSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9    

    def items(self):
        versions = Shortener.objects.exclude(creator = None).filter(active=True)[:20]
        return versions
    
    def lastmod(self, obj):
        return obj.created
        
    def location(self, obj):
        return reverse('selfurl:generate_click_record_pdf_view', args=[str(obj.short_url)])
    

    

    

    

    

               
    