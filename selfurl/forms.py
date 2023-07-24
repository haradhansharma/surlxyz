from django import forms
from .models import Shortener, Versions
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible, ReCaptchaV2Checkbox
from django.db.models import Q
from accounts.forms import DateInput

class SetExpireDateForm(forms.ModelForm):
    
    class Meta:
        model = Shortener
        fields = ('expires_at',)
        
        widgets = {                      
            'expires_at': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'birthdate', }),              
        }


class CreateVersionForm(forms.ModelForm):
    
    class Meta:
        model = Versions
        fields = ('version',)
        
        widgets = {                      
            'version': forms.TextInput(attrs={'placeholder': 'Write new version', 'class':'form-control', 'aria-label':'Version'}),                
        }
        
    def clean_version(self):
        version = self.cleaned_data['version']
        # Combine the filter conditions using Q objects
        existing_versions = Q(version=version)
        existing_short_urls = Q(short_url__iexact=version)

        # Check if the submitted version already exists in urlversion
        if Versions.objects.filter(existing_versions).exists():
            raise forms.ValidationError('This version already exists in urlversion.')

        # Check if the submitted version matches the slug field in Shortener
        if Shortener.objects.filter(existing_short_urls).exists():
            raise forms.ValidationError('The version already exists in the database.')


        return version
    

class ShortenerForm(forms.ModelForm):    
    long_url = forms.URLField(widget=forms.URLInput(
        attrs={"class": "form-control", "placeholder": "Your URL to shorten"}))
  
    
    
    class Meta:
        model = Shortener
        fields = ('long_url',)
        
class CheckingForm(forms.Form):   
    from django.contrib.sites.models import Site
    
    short_url = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(
        attrs={"class": "form-control rounded-0", 'placeholder': "Enter last part of url" }),
        label=Site.objects.get_current().domain + '/'
        )
    reasons = forms.CharField(
        label='Reasons you are reporting for',  # The label for the text field
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Reasons you are reporting for', 'class': 'form-control'}),  # Textarea widget with 4 rows
        max_length=500,  # Optionally, you can set the maximum length of the text
        required=True,  # Set to True if the field is required
        help_text="This report is requested to be done honestly. Because with this report, the target URL will be closed for all those who have taken our service to shorten it for their needs. Your dishonesty may cause us to lose business."
        
    )
    captcha = ReCaptchaField( widget=ReCaptchaV2Checkbox)  
    