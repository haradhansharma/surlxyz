from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, 
    UserChangeForm, 
    AuthenticationForm, 
    PasswordResetForm, 
    SetPasswordForm, 
    PasswordChangeForm
)
from main.context_processor import site_info
from .models import User, Profile
from .tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible, ReCaptchaV2Checkbox
from phonenumber_field.widgets import PhoneNumberPrefixWidget, RegionalPhoneNumberWidget, PhonePrefixSelect

class AvatarForm(forms.ModelForm):
    class Meta:
        
        
        model = Profile
        fields = ('avatar',)
        
        widgets = {  
            'avatar': forms.FileInput(attrs={ 'class':'form-control', 'aria-label':'Avatar' }),   
        }
        

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'organization', 'phone', ) 
        
        widgets = {                      
            'username': forms.TextInput(attrs={'placeholder': 'username', 'class':'form-control', 'aria-label':'username',  }),
            'first_name': forms.TextInput(attrs={'placeholder': 'first_name', 'class':'form-control', 'aria-label':'first_name' }),
            'last_name': forms.TextInput(attrs={'placeholder': 'last_name','class':'form-control', 'aria-label':'last_name', }), 
            'organization': forms.TextInput(attrs={'placeholder': 'organization','class':'form-control', 'aria-label':'organization', }), 
            # 'phone': forms.TextInput(attrs={'placeholder': 'phone','class':'form-control', 'aria-label':'phone', }), 
            'phone' : PhoneNumberPrefixWidget(initial='GB', attrs={'placeholder': 'Enter phone number', 'aria-label':'phone_number'}, number_attrs ={'class':'form-control'} , country_attrs={'class': 'input-group-text'}) ,
            
            'email': forms.EmailInput(attrs={'placeholder': 'email', 'class':'form-control', 'aria-label':'email' , }),     
            
        }
        labels = {                    
            'username':'Username',
            'first_name':'First name',
            'first_name':'Last Name',
            'organization':'Organization',
            'phone':'Phone',
            'email': 'Email',            
        }
        
# custom input typ        
class DateInput(forms.DateInput):
    input_type = 'date'       
   
        
class ProfileForm(forms.ModelForm):
    class Meta:       
        model = Profile
        fields = ('about','location','birthdate',)        
        widgets = {                      
            'about': forms.Textarea(attrs={'placeholder': 'about', 'class':'form-control', 'aria-label':'about', 'style':"height: 150px;" }),
            'location': forms.TextInput(attrs={'placeholder': 'location', 'class':'form-control', 'aria-label':'location' }),
            'birthdate': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'birthdate', }),            
            
        }
        labels = {                         
            'about': 'About',
            'location': 'Location',
            'birthdate': 'Birth Day', 
        }


class SetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)        
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control'})
        
        
        
class PasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)        
        self.fields['email'].widget = forms.EmailInput(attrs={ 'class':'form-control'}) 
        
        


class PasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True, 'class':'form-control'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control'})
        
        

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'
        
        
        
class UserCreationFormFront(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    username = forms.CharField(label = 'Username', widget=forms.TextInput(attrs={"class": "form-control" }))
    email = forms.EmailField(label = 'E-Mail Address', widget=forms.EmailInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(label = 'Password', widget=forms.PasswordInput(attrs={"class": "form-control" }))
    password2 = forms.CharField(label = 'Confirm Password', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    captcha = ReCaptchaField( widget=ReCaptchaV2Checkbox)   
    
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password1')
        
        if email and password:
            email_qs = User.objects.filter(email=email)
            if not email_qs.exists():
                pass    
            else:               
                is_active_qs = User.objects.filter(email=email, is_active=False).first()          
                if is_active_qs:    
                    subject = 'Account activation required!'  
                    current_site = Site.objects.get_current()  
                    message = render_to_string('emails/account_activation_email.html', {
                        'user': is_active_qs,                    
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(is_active_qs.pk)),
                        'token': account_activation_token.make_token(is_active_qs),                        
                    })
                    
                    is_active_qs.email_user(subject, message)                   
                    raise forms.ValidationError(f'You have an account already with this email. An account activation link has been sent to your mailbox {email}')
        return super(UserCreationFormFront, self).clean(*args, **kwargs)    

class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        
 
class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']            
        
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"  }))    
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    remember_me = forms.BooleanField(label = 'Remember me ', initial=False,  required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)     
    
    def clean(self, *args, **kwargs):        
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            email_qs = User.objects.filter(email=email)
            if not email_qs.exists():
                raise forms.ValidationError("The user does not exist")
            else:
                is_active_qs = User.objects.filter(email=email, is_active=False).first()
                if is_active_qs:
                    subject = 'Account activation required!'  
                    current_site = Site.objects.get_current()  
                    message = render_to_string('emails/account_activation_email.html', {
                        'user': is_active_qs,                    
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(is_active_qs.pk)),
                        'token': account_activation_token.make_token(is_active_qs),                        
                    })
                    
                    is_active_qs.email_user(subject, message)                      
                    raise forms.ValidationError(f'Account is not active, your need to activate your account before login. An account activation link has been sent to your mailbox {email}')                
                else:
                    user = authenticate(email=email, password=password)                      
                    
                    if not user:
                        raise forms.ValidationError("Incorrect password. Please try again!")    
        else:
            raise forms.ValidationError("Add you credentials!") 
                                           
        return super(LoginForm, self).clean(*args, **kwargs)
    
