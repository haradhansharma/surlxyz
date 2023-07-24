from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import activate, gettext_lazy as _

# Create your models here.
class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('closed', _('Closed')),
              
    )    
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField()
    email = models.EmailField()
    subject = models.CharField(max_length=251)  
    message = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.email})'
    
    
class Reply(models.Model):      
    thread = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name ='threads')   
    message = models.TextField()
    reply_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f'{self.message}'