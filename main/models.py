from django.db import models
from django.contrib.sites.models import Site
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.sites.managers import CurrentSiteManager
from phonenumber_field.modelfields import PhoneNumberField



from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import activate, gettext_lazy as _

from django.core.validators import FileExtensionValidator
from django.contrib.sites.models import Site



# Create your models here.
class ExSite(models.Model):    
    site = models.OneToOneField(Site, primary_key=True, verbose_name='site', on_delete=models.CASCADE, related_name='extend')
  
    site_description = models.TextField(max_length=500)
    site_meta_tag =models.CharField(max_length=255)
    site_favicon = models.ImageField(upload_to='site_image/')
    site_logo = models.ImageField(upload_to='site_image/')
    trademark = models.ImageField(upload_to='site_image/')
    slogan = models.CharField(max_length=150, default='')
    og_image = models.ImageField(upload_to='site_image/')
    mask_icon = models.FileField(upload_to='site_image/', validators=[FileExtensionValidator(['svg'])])    
    facebook_link = models.URLField()
    twitter_link = models.URLField()
    linkedin_link = models.URLField()    
    instagram_link = models.URLField()    
    
    email = models.EmailField()
    location = models.TextField()
    phone = models.CharField(max_length=16)    
    
    objects = models.Manager()
    on_site = CurrentSiteManager('site')
    
    def __str__(self):
        return self.site.__str__()  
    
    

    
   
        
    
        
     
  
  
