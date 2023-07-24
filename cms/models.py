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

from .mixins import (
    TitleAndSlugModelMixin, 
    CreatorModelMixin,    
    SitesModelMixin,
    IsActiveModelMixin,
    MenuModelMixin,
    SaveFromAdminMixin,
    DateFieldModelMixin,
    ) 

from main.agent_helper import get_ip

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


  
class Action(models.Model):
    VIEW = 'view'
    LIKE = 'like'
    ACTION_TYPES = (
        (VIEW, 'View'),
        (LIKE, 'Like')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')   
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action_type = models.CharField(max_length=4, choices=ACTION_TYPES, default=VIEW,db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)  
    
    
class Category(
    TitleAndSlugModelMixin, 
    CreatorModelMixin,    
    SitesModelMixin,
    IsActiveModelMixin,
    MenuModelMixin,
    DateFieldModelMixin,
    models.Model,
    SaveFromAdminMixin,    
    
    
    ):
    
    icon = models.CharField(_('FA Icon'), max_length=250, help_text=_('HTML Fontawesoome icon'), default='<i class="fa-solid fa-calendar-check"></i>')
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('Parent'))        
    add_to_cat_menu = models.BooleanField(default=True)  
    

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')    
        ordering = ['-created_at'] 
        
    def get_absolute_url(self):
        return reverse('cms:category_detail', args=[str(self.slug)])
    
   
    @property
    def have_items(self):
        if self.blogs_category.filter(status = 'published').exists():
            return True
        return False
        
    
    






class UserCMSManager(models.Manager):
    def foruser(self, user):
        # Filter pages based on the provided user
        return self.filter(creator=user)
    
 
    
    
    
class Page(   
    TitleAndSlugModelMixin, 
    IsActiveModelMixin,
    MenuModelMixin,
    SitesModelMixin,  
    CreatorModelMixin, 
    DateFieldModelMixin,
    models.Model,   
    SaveFromAdminMixin,        
    
    ):  
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('unpublished', _('UnPublished')),        
    )    
    top_banenr = models.ImageField(_('Top Banner'), upload_to='blog/top_banenr/', null=True, blank=True)
    top_tagline = models.CharField(max_length=40, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('Parent'))
    body = models.TextField(verbose_name=_('Body'))
    meta_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')   
    actions = GenericRelation(Action)
    consent_required = models.BooleanField(default=False)
    objects = models.Manager()  # Fallback manager to query all pages
  
    
    # Manager for filtering pages based on user to call Page.userpages.foruser(request.user)
    userpages = UserCMSManager()
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:page_detail', args=[str(self.slug)])

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'        
        ordering = ['-created_at']           
            
    def view(self, request):
        # create a new action object for this view
        Action.objects.create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_ip(request),
            action_type=Action.VIEW
        )       


    def like(self, request):
        Action.objects.create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_ip(request),
            action_type=Action.LIKE
        )
        
    def dislike(self, request):
        Action.objects.get(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_ip(request),
            action_type=Action.LIKE
        ).delete()
        
    @property
    def total_view(self):
        total = Action.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            action_type=Action.VIEW
        ).count()
        return total
    
    @property
    def total_like(self):
        total = Action.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            action_type=Action.LIKE
        ).count()
        return total
    
       
        
    
        
        
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')
    
class UnPublishedManager(models.Manager):
    def get_queryset(self):
        return super(UnPublishedManager, self).get_queryset().filter(status='unpublished')
    
class DraftManager(models.Manager):
    def get_queryset(self):
        return super(DraftManager, self).get_queryset().filter(status='draft').order_by('-updated_at')
        
        
class Blog(
    TitleAndSlugModelMixin,
    MenuModelMixin,
    SitesModelMixin,
    CreatorModelMixin, 
    DateFieldModelMixin,
    models.Model,
    SaveFromAdminMixin,    
    
    
    ):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('unpublished', _('UnPublished')),        
    )
    
    feature = models.ImageField(_('Feature Image'), upload_to='blog/feature_image/')
    
    
    categories = models.ManyToManyField(
        Category,
        blank=True,
        db_index=True,
        verbose_name=_('Categories'),
        related_name='blogs_category'
      
    )  
    
    body = models.TextField(verbose_name=_('Body'))  
        
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)   
    actions = GenericRelation(Action)
    
    
    

    
    
    def view(self, request):
        # create a new action object for this view
        Action.objects.create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_ip(request),
            action_type=Action.VIEW
        )       


    def like(self, request):
        Action.objects.create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_ip(request),
            action_type=Action.LIKE
        )
        
    def dislike(self, request):
        Action.objects.get(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_ip(request),
            action_type=Action.LIKE
        ).delete()
        
        
    @property
    def total_view(self):
        total = Action.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            action_type=Action.VIEW
        ).count()
        return total
    
    @property
    def total_like(self):
        total = Action.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            action_type=Action.LIKE
        ).count()
        return total      
    
    
      
    @property  
    def get_content_type(self):
        return ContentType.objects.get_for_model(self)
    
    
    objects = models.Manager()#default manager
    published = PublishedManager()#Cutom Manager
    unpublished = UnPublishedManager()#Cutom Manager    
    draft = DraftManager()#Cutom Manager
    
    # Manager for filtering pages based on user to call Blog.userblogs.foruser(request.user)
    userblogs = UserCMSManager()
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:blog_details', args=[str(self.slug)])       

    def like_or_dislike_url(self):
        return reverse('cms:like_or_dislike', args=[int(self.get_content_type.id), str(self.id)])        
    
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        ordering = ['-created_at']
        


       
  
def validate_file_size(value):
    filesize= value.size

    if filesize > 5*1024*1024:
        raise ValidationError(_("The maximum file size that can be uploaded is 5MB"))
      
        
