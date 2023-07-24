from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'created_at' )  
    search_fields = ('name', 'phone_number', 'email', 'message' )    
    ordering = ('-created_at',)