from django.contrib import messages
from urllib.parse import urlparse
from django.http import Http404, HttpResponseRedirect
# from selfurl.decorators import coockie_exempts, coockie_required
from .models import *
from .forms import UserCreationFormFront, PasswordChangeForm, UserForm, ProfileForm, AvatarForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from main.context_processor import site_info
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied


@login_required
def delete_avatar(request):    
    user = request.user
    profile = user.get_profile
    profile.avatar.delete()
    profile.avatar = ''
    profile.save()
    
    return HttpResponseRedirect(reverse('accounts:profile_setting', args=[str(user.id)]))


@login_required
def profile_setting(request, id):  
    if id == str(request.user.id):   
        pass
    else:
        raise PermissionDenied      
    
    site = site_info() 
    site['title'] = f'Profile Settings'
    site['description'] = f'Take control of your online presence with our profile settings page. Customize your profile, privacy settings, and communication preferences to tailor your experience. Safeguard your data and manage your interactions effortlessly. Unlock the power of personalization at your fingertips'
    
    
     
    if request.method == "POST":
        if 'user_form' in request.POST:
            user_form = UserForm(request.POST, instance=request.user)
                 
            if user_form.is_valid():                
                user_form.save()
                messages.success(request,('Your profile was successfully updated!'))                
            else:
                messages.error(request, 'Invalid form submission.')                
                messages.error(request, user_form.errors)    
                
        if 'profile_form' in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user.profile)   		    
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request,('Your profile data was successfully updated!'))
            else:
                messages.error(request, 'Invalid form submission.')
                messages.error(request, profile_form.errors)       
                
        if 'avatar_form' in request.POST:
            avatar_form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
  
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request,('Avatar Updated successfully!'))
            else:
                messages.error(request, 'Invalid form submission.')
                messages.error(request, avatar_form.errors)    
                
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)    
    avatar_form = AvatarForm(instance=request.user.profile)        
 
    context = {
        "user":request.user,
        "user_form":user_form,
        "profile_form":profile_form,  
        'avatar_form' : avatar_form,     
        'site_data' : site ,               
    }
    response = render(request, 'registration/profile_settings.html', context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 

@login_required
def password_change(request):        
    
    site = site_info() 
    
    site['title'] = 'Change Password'
    site['description'] = 'Securely update your password on our platform. Protect your account with a new, strong password to ensure the safety of your personal information. Change password hassle-free and strengthen your online security today.'
    
    
    if request.method == "POST":        
        password_form = PasswordChangeForm(user=request.user, data=request.POST)        
        if password_form.is_valid():            
            password_form.save()            
            update_session_auth_hash(request, password_form.user)            
            messages.success(request,('Your password was successfully updated!')) 
        else:
            messages.error(request, 'Invalid form submission.')            
            messages.error(request, password_form.errors)         
        return HttpResponseRedirect(reverse('accounts:change_pass'))    
    password_form = PasswordChangeForm(request.user)  
    
    context = {
        "user":request.user,        
        "password_form":password_form,
        'site_data' : site ,
    }
    response = render(request, 'registration/change_pass.html', context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    
   
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books 
        site_data = site_info()    
        site_data['title'] = 'Password reset completed'     
        site_data['description'] = 'Password reset successfully! Your account is now secure. Log in with your new credentials and regain access to your account. Stay protected with our secure password management tools.'     
        

        context['site_data'] = site_data
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return context
    

class CustomPasswordResetView(PasswordResetView):
    from .forms import PasswordResetForm
    
    #overwriting form class to take control over default django
    form_class = PasswordResetForm
   
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        site_data = site_info()   
        site_data['title'] = 'Reset your password'
        site_data['description'] = 'Reset your password securely and regain access to your account with our user-friendly password reset form. Safeguard your data and follow a simple step-by-step process to create a new password. Experience hassle-free account recovery and ensure the protection of your valuable information. Reset your password now and get back to enjoying our platform with peace of mind'

        context['site_data'] = site_data
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return context
    

class CustomPasswordResetDoneView(PasswordResetDoneView):
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        site_data = site_info()   
        site_data['title'] = 'Password reset done'
        site_data['description'] = 'Password Reset Done - Your password has been successfully reset. '

        context['site_data'] = site_data
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return context
    

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    from .forms import SetPasswordForm
    
    #overwriting form class to take control over default django
    form_class = SetPasswordForm
    
    def get_context_data(self, **kwargs):
        
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books  
        
        site_data = site_info()   
        site_data['title'] = 'Password reset confirm'
        site_data['description'] = 'Confirm your password reset. '

        context['site_data'] = site_data
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        
        return context

    


class CustomLoginView(LoginView):
    #To avoid circular reference it is need to import here
    from .forms import LoginForm
    
    #overwriting form class to take control over default django
    form_class = LoginForm 
    
    
    #overwriting to set custom after login path
    next_page = ''
    
    
    #taking control over default of Django  
    def form_valid(self, form): 
        
        #set after login url 
        self.next_page = reverse_lazy('accounts:profile_setting', args=[str(form.get_user().username)])           
        
        #rememberme section        
        remember_me = form.cleaned_data.get('remember_me')  
        # as during signup user need to accept our policy so we can set term accepted 
        self.request.session['term_accepted'] = True   
        
        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)
            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True  
        # self.request.session.set_test_cookie()
        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)
    
    
    def get_context_data(self,  **kwargs):
        
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        

        site_data = site_info()   
        site_data['title'] = 'Unlock Your World of Possibilities - Log In Now!'
        site_data['description'] = 'Welcome to our login page - where your online journey begins. Log in to access a world of personalized features and exclusive benefits. Securely manage your account and explore a seamless online experience. Join us today!'

        context['site_data'] = site_data
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'index, follow'
        return context




def signup(request):  
    
    site_data = site_info()   
    site_data['title'] = 'Unlock the Power of Link Management | Join Our URL Shortener Community Today!'
    site_data['description'] = 'Sign up for free and gain access to advanced link management tools, click analytics, and URL customization. Join our URL shortener community to enhance your online presence and track your links effortlessly.'
        
    if request.method == 'POST':
        current_site = get_current_site(request)
        form = UserCreationFormFront(request.POST)
        if form.is_valid():     
            new_user = form.save(commit=False)    
            new_user.is_active = False       
            new_user.save()
            subject = 'Account activation required!' 
            message = render_to_string('emails/account_activation_email.html', {
                'user': new_user,                    
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user),                
            })
            
            new_user.email_user(subject, message)            
            messages.success(request, 'Please Confirm your email to complete registration.') 
            return HttpResponseRedirect(reverse_lazy('login'))
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)
    else: 
        form = UserCreationFormFront()
    context = {
        'form': form,
        'site_data' : site_data ,      
        
    }
    response = render(request, 'registration/register.html', context = context) 
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, ('Your account have been confirmed.'))
        return HttpResponseRedirect(reverse_lazy('login'))
    else:
        messages.warning(request, ('Activation link is invalid!'))
        return HttpResponseRedirect(reverse_lazy('home:home'))
        
    




    
    
    
    
    
    
    

