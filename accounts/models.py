from django.db import models
# from bds.models import BdService, PaymentMethod

import uuid
from django.db import models
from django.urls import reverse
from PIL import Image
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, Resize, ProcessorPipeline
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


from django.utils import timezone

class QIUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super(QIUserManager, self).create_user(username, email, password, **extra_fields)

    def create_superuser(self, username = None, email=None, password=None, **extra_fields):
        return super(QIUserManager, self).create_superuser(username, email, password, **extra_fields)



class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    username = models.CharField(
        _("username"),      
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
   
    email = models.EmailField('E-Mail Address', unique=True)
    phone = PhoneNumberField('Phone', blank=True, null=True)
    organization = models.CharField(max_length=252, null=True, blank=True)   
     
    
    objects = QIUserManager()

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def get_absolute_url(self):        
        return reverse('accounts:user_link', args=[str(self.id)])
    
    @property
    def is_paid(self):
        return False
    
    @property
    def get_profile(self):
        return self.profile   
         
        
    
class CustomResizeToFill(Resize):
    def process(self, img):
        if self.height is None:
            self.height = img.height

        if self.width is None:
            self.width = img.width

        img.thumbnail((self.width, self.height), Image.BICUBIC)

        return img

    
class Profile(models.Model):
    # It is beeing created autometically during signup by using signal.
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = ProcessedImageField(upload_to='profile_photo',
                    processors=ProcessorPipeline([CustomResizeToFill(200, 200)]),
                    format='JPEG',
                    options={'quality': 60})
    about = models.TextField('About Me', max_length=500, blank=True, null=True)
    
    
    location = models.CharField('My Location', max_length=30, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)  
    
    def __str__(self):
        return 'Profile for ' +  str(self.user.email)  
    


