from django import forms
from .models import ContactMessage, Reply
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget, RegionalPhoneNumberWidget, PhonePrefixSelect
from captcha.widgets import ReCaptchaV2Invisible, ReCaptchaV2Checkbox
from captcha.fields import ReCaptchaField


class ThreadReplyForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label='')  
    class Meta:
        model = Reply
        fields = ['message']
        
        widgets = {
            'message': forms.Textarea(attrs={'rows':'3','placeholder': 'Message', 'aria-label':'message', 'class': 'form-control' }), 
        }
        labels = {
            'message' : '',
            'captcha' : ''
        }


class ContactUsForm(forms.ModelForm):    
    captcha = ReCaptchaField( widget=ReCaptchaV2Checkbox)  
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone_number', 'email', 'subject', 'message']        
        
        widgets = {                      
            'name': forms.TextInput(attrs={'placeholder': 'Name', 'aria-label':'Name', 'class': 'form-control'  }),  
            'phone_number' : PhoneNumberPrefixWidget(initial='GB', attrs={'placeholder': 'Enter phone number', 'aria-label':'phone_number'}, number_attrs ={'class':'form-control'} , country_attrs={'class': 'input-group-text'}) ,
            'email': forms.EmailInput(attrs={'placeholder': 'email',  'aria-label':'email' , 'class': 'form-control' }),                
            'subject': forms.TextInput(attrs={'placeholder': 'Subject',  'aria-label':'subject', 'class': 'form-control'  }),            
            'message': forms.Textarea(attrs={'rows':'5','placeholder': 'Message', 'aria-label':'message', 'class': 'form-control' }), 
        }
        
        PhoneNumberPrefixWidget(attrs={'placeholder': 'Enter phone number'})