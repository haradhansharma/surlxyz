from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from .forms import *
from django.contrib import messages
from django.conf import settings
from main.context_processor import site_info
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from main.templatetags.selfurl_tags import base64_encode, base64_decode
from main.helper import (
 
    custom_send_mass_mail,
    has_threads, 
    
    )
@login_required
def post_reply(request, id):
    template_name = 'contact/post_reply.html'

    if request.method == 'POST':
        thread = ContactMessage.objects.get(id = id)
        form = ThreadReplyForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            Reply.objects.create(thread = thread, message = message, reply_email=request.user.email  )
            reply_instruction = request.POST.get('status')

            if reply_instruction:
                thread.status = 'close'
                thread.save()    
            context = {
                'reply' : message,                   
            }
            return render(request, template_name, context=context)            
        else:
            messages.error(request, 'There was an error with your submission. Please try again.')
            messages.error(request, form.errors)  
            
    
    response = render(request, template_name, context={}) 
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 
    
@login_required
def get_reply_form(request, id):
    
    template_name = 'contact/thread_reply_form.html'
    form = ThreadReplyForm()
    thread = ContactMessage.objects.get(id = id)
    
    context = {
        'form' : form,
        'thread' : thread
       
    }
    return render(request, template_name, context=context)


 
@login_required
def threads(request, email): 
    if email != base64_encode(request.user.email) or not request.user.is_staff or not request.user.is_superuser:
        raise PermissionDenied
    
    if not has_threads(request.user.email):
        raise Http404
    
    template_name = 'contact/threads.html'
     
    site = site_info()
    site['title'] = 'Threads'
    site['description'] = 'All Threads of the login user if exists.'
    if request.user.is_staff or request.user.is_superuser:
        threads = ContactMessage.objects.all().order_by('-created_at').prefetch_related('threads')
    else:        
        threads = ContactMessage.objects.filter(email = base64_decode(email)).order_by('-created_at').prefetch_related('threads')
        
        
    page = request.GET.get('page', 1)
    paginator = Paginator(threads, 10)
    try:
        threads = paginator.page(page)
    except PageNotAnInteger:
        threads = paginator.page(1)
    except EmptyPage:
        threads = paginator.page(paginator.num_pages)   
    
    
    context = {
        # 'form' : form,
        'site_data' : site,
        'threads' : threads
    }
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 


# Create your views here.
def contact(request):
    
    template_name = 'contact/contact.html' 
    form = ContactUsForm()
    site_data = site_info()
        
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()            
            messages.success(request, 'Currently we are not taking email. Please sent your query to contact@selfurl.xyz')
            return redirect(reverse_lazy('contact:contact'))
        
            # email_messages = []
            
            # from_email = settings.DEFAULT_FROM_EMAIL               
            
            # # Send email to the site admin
            # admin_subject = f'{site_data["name"]} - New contact form submission'
            # admin_message = f"Name: {form.cleaned_data['name']}\nEmail: {form.cleaned_data['email']}\n\nMessage: {form.cleaned_data['message']}"        
            # admin_reply_to = [form.cleaned_data['email']]        
            # admin_mail = [site_data.get('email')]
            
            
            # email_messages.append((admin_subject, admin_message, from_email, admin_mail , '',  admin_reply_to, ''))
            
            # visitor_subjct = f'{site_data["name"]} - Greetings from {site_data["name"]}!' 
            # visitor_message = f"Dear {form.cleaned_data['name']},\n\nThank you for reaching out to us through our website." 
            # visitor_message += f"We appreciate your interest in {site_data.get('name')}!\n\n"
            # visitor_message += f"This email is to acknowledge that we have received your contact form submission. Please note that this is a no-reply email, "
            # visitor_message += f"so there's no need to reply to it.\n\nA thread have been created at {request.build_absolute_uri(reverse('contact:threads', args=[base64_encode(request.user.email)]))}"
            # visitor_message += f" . You may follow responses there.\n\nOur team is currently reviewing your message, and we will get back to you soon with a response at the designated thread. "
            
            # visitor_message += f"We strive to provide excellent service and address your inquiry promptly.\n\nOnce again, we thank you for getting in touch with us. "
            # visitor_message += f"We look forward to connecting with you!\n\nBest regards,\nThe {site_data.get('name')} Team"
            # visitor_mail = [form.cleaned_data['email']]
            
            # email_messages.append((visitor_subjct, visitor_message, from_email, visitor_mail, '', '', ''))        

            # custom_send_mass_mail(email_messages, fail_silently=False)
            
            
        else:   
            messages.error(request, 'There was an error with your submission. Please try again.')
            
    
       
        
    site = site_info()
    site['title'] = 'Connecting with Us, Simplifying Your URLs'
    site['description'] = f'Contact {site.get("name")} for any inquiries, feedback, or collaboration opportunities. Our dedicated team is here to assist you. Reach out to us through the provided contact details or fill out the contact form on our page. We look forward to hearing from you and providing the support you need.'
    
    
    context = {
        'form' : form,
        'site_data' : site
    }
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 
