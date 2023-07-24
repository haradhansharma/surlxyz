from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

class Shortener(models.Model):
    '''
    Creates a short url based on the long one    
    created -> Hour and date a shortener was created     
    times_followed -> Times the shortened link has been followed
    long_url -> The original link
    short_url ->  shortened link https://domain/(short_url)
    ''' 
    
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    
    clicked = models.PositiveIntegerField(default=0)
    
    long_url = models.URLField(max_length=2000, db_index=True)
    short_url = models.SlugField(max_length=15, unique=True, db_index=True)
    
    active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
        
    ip = models.CharField(max_length=152)
    user_agent = models.TextField()
    country = models.CharField(max_length=150)
    lat = models.CharField(max_length=150)
    long = models.CharField(max_length=150)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ["-created"]


    def __str__(self):
        return f'{self.long_url} to {self.short_url}'
    
    
    def save(self, *args, **kwargs):                           
        self.short_url = slugify(self.short_url)
        super().save(*args, **kwargs)
        
class Versions(models.Model):
    url = models.ForeignKey(Shortener, on_delete=models.CASCADE, related_name='urlversion')
    version = models.SlugField(db_index=True)
    clicked = models.PositiveIntegerField(default=0)    
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created"]


    def __str__(self):
        return f'{self.url} version {self.version}' if self.url else self.version
    
        
class ReportMalicious(models.Model):
    url = models.ForeignKey(Shortener, on_delete=models.CASCADE, related_name='reporturl')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='reportuser')
    reasons = models.TextField('Reasons you are reporting for', help_text='This report is requested to be done honestly. Because with this report, the target URL will be closed for all those who have taken our service to shorten it for their needs. Your dishonesty may cause us to lose business.')
    checked = models.BooleanField(default=False)
    check_decision = models.CharField(max_length=50)
    checked_at = models.DateTimeField(null=True, blank=True)    
    created = models.DateTimeField(auto_now_add=True)
        
class VisitorLog(models.Model):
    shortener = models.ForeignKey(Shortener, on_delete=models.CASCADE, related_name='visitorlogs') 
    user_agent = models.BinaryField()
    geo_data = models.BinaryField()  
    visited = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        ordering = ["-visited"]
        
    
    
class VisiLogSecretKey(models.Model):
    v_log = models.OneToOneField(VisitorLog, related_name='logkey', on_delete=models.CASCADE)
    key = models.BinaryField()
    