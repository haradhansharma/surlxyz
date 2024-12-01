import base64
import random
import string
from django.conf import settings
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from main.context_processor import site_info
from django.contrib import messages
from django.views.decorators.cache import cache_control
from main.helper import check_exists, is_reported
from .forms import (
    CheckingForm, 
    ShortenerForm, 
    CreateVersionForm, 
    SetExpireDateForm
)
from .models import (
    Shortener,
    VisiLogSecretKey, 
    VisitorLog, 
    ReportMalicious,
    Versions
)
from main.agent_helper import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import arrow
from cryptography.fernet import Fernet
from django.db.models import Count, Q
from django.core.mail import send_mass_mail

import io
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, KeepTogether, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, String, Circle, Line
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from django.core.exceptions import PermissionDenied

 
    
    
def redirect_url(request, brand=None, short_url = None): 
    if request.user_agent.is_bot:
        return HttpResponse('Request not accepted! Please contact US!')   
    
    found = '' 
    
    try:
        # Query the Shortener model
        shortener = Shortener.objects.get(short_url=short_url, active=True)
        found = 'main_short'
    except Shortener.DoesNotExist:
        try:
            # Query the Versions model
            version = Versions.objects.get(version=short_url)
            shortener = version.url
            found = 'version_short'
        except Versions.DoesNotExist:
            raise Http404('Not Found!')
        
    # if url reported as malicious it will not redirect
    if is_reported(shortener.long_url):
        shortener.active = False
        shortener.save()
        raise Http404('The Redirector is inactive')
    
    #if expires_at none it means it will not expire anymore
    if not shortener.expires_at:
        shortener.active = True
        shortener.save()
    else:
        # expires_at less then current date it will not redirect and make inactive here.
        # So will do not need to run cronjob
        if shortener.expires_at < timezone.now():        
            shortener.active = False
            shortener.save()
            raise Http404('The Redirector is inactive')       

    
    shortener.clicked += 1
    shortener.save()
    
    if found == 'version_short':
        version.clicked += 1
        version.save()
        
        
    # Generate a random secret key for the user
    user_secret_key = Fernet.generate_key()
 

    # Create a Fernet cipher suite using the user secret key
    cipher_suite = Fernet(user_secret_key)
    
    
    user_agent = get_agent(request)   
    # Convert the user_agent dictionary to a JSON string
    user_agent_json = json.dumps(user_agent)
    # Encrypt the user_agent dict
    encrypted_user_agent = cipher_suite.encrypt(user_agent_json.encode())    
    
    geodata = get_geodata(request)    
    # Convert the geodata dictionary to a JSON string
    geodata_json = json.dumps(geodata)
    # Encrypt the geodata dict
    encrypted_geodata = cipher_suite.encrypt(geodata_json.encode())  
    
    encoded_key = base64.b64encode(user_secret_key)    
  
        
    visitor_log = VisitorLog.objects.create(
        shortener=shortener,           
        user_agent = encrypted_user_agent, 
        geo_data = encrypted_geodata,        
    )  
    # Create a VisiLogSecretKey object and associate it with the VisitorLog instance
    VisiLogSecretKey.objects.create(v_log=visitor_log, key=encoded_key)
         
    
    redirect_to = shortener.long_url   
    
    return HttpResponseRedirect(redirect_to)   

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)   
def log_details(request, short_url):  
    if request.user.is_paid or request.user.is_superuser:
        pass
    else:
        raise PermissionDenied
    
    shortener = Shortener.objects.prefetch_related('visitorlogs__logkey', 'reporturl').get(short_url = short_url)
    if is_reported(shortener.long_url):
        raise Http404
    visit_logs = shortener.visitorlogs.all()
    for vl in visit_logs:
        secret_key = base64.b64decode(vl.logkey.key)
        cipher_suite = Fernet(secret_key)        
        decrypted_user_agent = json.loads(cipher_suite.decrypt(vl.user_agent))
        decrypted_geodata = json.loads(cipher_suite.decrypt(vl.geo_data))    
        
        vl.ip = decrypted_geodata.get('IPv4')
        vl.country = decrypted_geodata.get('country_name')
        vl.city = decrypted_geodata.get('city')
        vl.postal = decrypted_geodata.get('postal')
        vl.state = decrypted_geodata.get('state') 
        vl.lat = decrypted_geodata.get('latitude')
        vl.long = decrypted_geodata.get('longitude')
        vl.user_usage = decrypted_user_agent.get('user_usage')
        vl.user_browser = str(decrypted_user_agent.get('user_browser')[0]) +'-'+ str(decrypted_user_agent.get('user_browser')[2])
        vl.user_os = str(decrypted_user_agent.get('user_os')[0]) +'-'+ str(decrypted_user_agent.get('user_os')[2])
        vl.user_device = str(decrypted_user_agent.get('user_device')[0]) +'-'+ str(decrypted_user_agent.get('user_device')[2])    

        
    #Paginated response
    page = request.GET.get('page', 1)
    paginator = Paginator(visit_logs, 10)
    try:
        visit_logs = paginator.page(page)
    except PageNotAnInteger:
        visit_logs = paginator.page(1)
    except EmptyPage:
        visit_logs = paginator.page(paginator.num_pages)
        
    # Every time someone clicks on your short URL, our technology will keep track. It doesn't matter if it came from the same device or from the same person.
    # Visitor Logs of shorten URL-
    
    context = {             
        'site_data' : site_info(),                  
        'visit_logs' : visit_logs,
        'short_url' : short_url,
        'reports':  shortener.reporturl.all()[:10],
        'clicked':  shortener.clicked          
            }
    response =  render(request, 'selfurl/log_details.html', context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response

    
    
@login_required
def set_expire(request, id):
    """
    This function sets the expiration date for a shortened URL.

    Args:
        request (django.http.HttpRequest): The HTTP request object.
        id (int): The ID of the shortened URL.

    Returns:
        django.http.HttpResponse: The HTTP response object.
    """
    template = "selfurl/set_expire.html"
    form = SetExpireDateForm()
    item = Shortener.objects.get(id =id)
   
    # If the request method is POST, then process the form data.
    
    if request.method == 'POST':
        form = SetExpireDateForm(request.POST)
        if form.is_valid(): 
            expires_at = form.cleaned_data["expires_at"]  
            
            # Set post data as expire data
               
            item.expires_at = expires_at
            
            # If the expiration date is in the future or is not set,
            # and the shortened URL is not reported as malicious,
            # then set the shortened URL to active.
            
            if (not expires_at or expires_at > timezone.now() ) and not is_reported(item.long_url):
                item.active = True
            else:
                item.active = False
             
            # Update Item   
            item.save()
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)  
        
        # Get the updated shortened URL object.
        
        item.refresh_from_db()  
 
        # We will not pass get form in post request
        # to control template code as it is requesting by HTMX.
        # And we will return for post request
        
        context = {            
            'item' : item            
        }        
        response = render(request, template, context = context) 
    
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
    
    # As the function is calling by HTMX will will return 
    # form and item both fot get request
    # it suports template code control.
            
    context = {
        'form' : form,
        'item' : item        
    }    
    return render(request, template, context = context)

def get_data_versions(request, short_url):
    data = get_object_or_404(Shortener.objects.prefetch_related('urlversion'), short_url=short_url)
    if is_reported(data.long_url):
        raise Http404
    versions = data.urlversion.all()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(versions, 10)
    try:
        versions = paginator.page(page)
    except PageNotAnInteger:
        versions = paginator.page(1)
    except EmptyPage:
        versions = paginator.page(paginator.num_pages)   
        
    return data, versions

@login_required    
def create_version(request, short_url):
    template = 'selfurl/create_versions.html'    
    form = CreateVersionForm()
   
    data, versions = get_data_versions(request, short_url)
    
    if is_reported(data.long_url):
        raise Http404
        
    if request.method == 'POST':
        form = CreateVersionForm(request.POST)
        if form.is_valid():   
            #checking it is already exists in Shortener or Version database in form lavel       
            version = form.cleaned_data["version"]   
            new_version = data.urlversion.create(version=version)
            new_version.save()            
          
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)   
            
        #to get latest data   
        data, versions = get_data_versions(request, short_url)
              
        context = {
            'data' : data,  
            'versions' : versions         
        }        
        response = render(request, template, context = context)   
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
    
    if 'getpage' in request.GET: 
        context = {
            'data' : data,
            'versions' : versions,           
        }
        return render(request, 'selfurl/versions_table_body.html', context = context)
    context = {
            'data' : data,
            'versions' : versions,
            'form' : form
        }
    
    response = render(request, template, context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response

@login_required   
def versions(request, short_url): 
    template = 'selfurl/versions.html'
    
    site = site_info() 
    
    site['title'] = f'Versions of {short_url}'
    site['description'] = f'Explore and manage multiple versions of your shortened URLs with ease. Our URL Versions feature allows registered users to customize and monitor different variations of their links. Track click analytics, set expiration dates, and create branded paths for enhanced branding. Experience comprehensive URL management with our secure and user-friendly platform.'
    
    
    data, versions = get_data_versions(request, short_url) 
    
    if is_reported(data.long_url):
        raise Http404
    
    context = {
        'data' : data,
        'site_data' : site,
        'versions' : versions
    }
    
    response = render(request, template, context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


def makeshort(request):
    #Should have oportunity to disput if
    
    template = 'selfurl/makeshort.html'
    report_limit = 3
    form = ShortenerForm()  
    if request.method == 'POST':
        form = ShortenerForm(request.POST)
        if form.is_valid():
            short_url = ''.join(random.choice(string.ascii_letters) for x in range(6))                    
            long_url = form.cleaned_data["long_url"]            
            short_url = check_exists(short_url)
            
            '''
            if this url reported by anybody cannot be added further.          
            '''
            
            # data = ReportMalicious.objects.filter(url__long_url=long_url)
           
            if is_reported(long_url):
                messages.error(request, f'The URL you are trying to shortened was reported as malicious! Request is rejected! Please be noted, if you have more than {int(report_limit)} reported url, your account can be banned!')
                context = { 'form': form, }
                return render(request, template, context = context)
        
            
            
            '''
            If this user shortend this url then will show that result
            Otherwise will save new and show new url
            '''
                
            try:                
                if request.user.is_authenticated:
                    data = Shortener.objects.get(long_url = long_url, creator = request.user)
                else:
                    data = Shortener.objects.get(long_url = long_url, creator = None)                    
                     
                context = {            
                    'data': data,
                    'form': form,                
                    }
                return render(request, template, context = context)
            except:
                user_agent = get_agent(request)       
                geodata = get_geodata(request)     
                
                new_url = Shortener(
                    long_url=long_url, 
                    short_url=check_exists(short_url), 
                    creator = request.user if request.user.is_authenticated else None, 
                    ip = get_ip(request), 
                    user_agent = user_agent, 
                    country = geodata.get('country_code'),  
                    lat = geodata.get('latitude'), 
                    long =  geodata.get('longitude')
                )
                                   
                new_url.save()   
                data = new_url                  
                          
                context = {            
                    'data': data,
                    'form': form,                           
                    }
                return render(request, template, context = context) 
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)   

    
    
    context = {
        'form': form,
        
    }
    
    response = render(request, template, context = context)
    response['X-Robots-Tag'] = 'index, follow'
    return response

@login_required
def deactivate_shorten(all_long_url, user, reasons):
    
    """
    Deactivate the provided URL objects, create or update ReportMalicious objects,
    and send a mass email to the creators of the deactivated URLs.

    Parameters:
        all_long_url (QuerySet): QuerySet of URL objects to be deactivated.
        user (User): The user who reported the URLs as malicious.
        reasons (str): Reasons for reporting the URLs as malicious.

    Returns:
        str: A confirmation message indicating that the URLs have been deactivated.
    """  
   
    
    # List to store the email data
    # This creates a list to store the email data, which will be used to send a mass mail to all creators of the deactivated URLs.
    email_data = []
    
    # Compose the mail message and add it to the email_data list
    # This creates a mail message and adds it to the email_data list. The mail message includes the blocked URL, the reason for blocking the URL, and a warning to users about the ethical use of the URL shortener.
    mail_subject = 'URL Deactivation Notification'
    mail_message = 'We have blocked the following URL: {}\nReason: {}\n\nPlease use URL shortner ethically! URL shorteniing for illegal use is not accepted!\n\nOperation Team!'

    for url in all_long_url:      
        
        # Use get_or_create to simplify the logic of creating or updating the ReportMalicious object
        # This uses the `get_or_create` method to simplify the logic of creating or updating the ReportMalicious object. The `get_or_create` method only makes a single database query, even if the object already exists. This further improves performance.
        report_malicious, created = ReportMalicious.objects.get_or_create(url=url, user=user, defaults={'reasons': reasons})
        
        if not created:
            # If the object already exists, update the reasons
            # If the ReportMalicious object already exists, the `reasons` field is updated with the new reasons.
            report_malicious.reasons = reasons
            
            # If again reported as malicious we set again as created
            report_malicious.checked = False
            report_malicious.check_decision = '' 
            
                       
            report_malicious.save()
         
        
        # Fetch the creator of each URL
        # This fetches the email address of the creator of each URL.
        creator_email = url.creator.email if url.creator else None
        
        # Append the email data to the list if there is assigned creator
        # This appends the email data to the email_data list.
        # But we will not send repeat email.
        if creator_email and url.active:
            email_data.append((mail_subject, mail_message.format(url, reasons), settings.DEFAULT_FROM_EMAIL, [creator_email]))
    
    # Bulk update all_long_url to set active=False
    # This updates the active status of all URLs in the all_long_url list to False.
    all_long_url.update(active=False)
    
    
    if email_data:
        # Send mass mail to all creators
        # This sends a mass mail to all creators of the deactivated URLs.
        send_mass_mail(email_data, fail_silently=True)
    
    return 'We have blocked this URL, and it is not available now! Stay Safe!'


def get_all_long(long_url):
    """
    Retrieve all URL objects associated with the given long_url.

    Parameters:
        long_url (str): The long URL for which associated Shortener objects are to be retrieved.

    Returns:
        QuerySet: A Django QuerySet containing all the Shortener objects associated with the given long_url.
    """
    # Filter the Shortener model based on the provided long_url and retrieve all matching objects.
    # The resulting QuerySet contains all URL objects that have the specified long_url.
    return Shortener.objects.filter(long_url=long_url)

@login_required
def malicious_submit(request):
    # As it is request by HTMX
    if not request.user.is_authenticated:
        return HttpResponse('Request not allowed!')
    
    template = 'selfurl/malicious_submit.html'
    
    # Create a CheckingForm instance to handle the user's input data
    form = CheckingForm()     
    
    if request.method == 'POST':        
        form = CheckingForm(request.POST)

        if form.is_valid():           
            # Extract cleaned data from the form
            short_url = form.cleaned_data["short_url"]
            reasons = form.cleaned_data["reasons"]
            
            # Find the Shortener object associated with the provided short_url
            shortener = Shortener.objects.filter(short_url=short_url)      
                       
            if shortener.exists():  
                # If the short URL is found, get the associated long URL and deactivate all its URLs
                long_url = shortener.first().long_url
                all_long_url = get_all_long(long_url)                
                deactivated_message = deactivate_shorten(all_long_url, request.user, reasons)                 
                messages.warning(request, deactivated_message)
            else:
                # If the short URL is not found in the Shortener model, search in the Versions model
                versions = Versions.objects.filter(version=short_url)
                
                if versions.exists():
                    # If the short URL is found in the Versions model, get the associated long URL and deactivate all its URLs
                    long_url = versions.first().url.long_url
                    all_long_url = get_all_long(long_url)
                    deactivated_message = deactivate_shorten(all_long_url, request.user, reasons)                 
                    messages.warning(request, deactivated_message)
                else:                    
                    messages.warning(request, 'Url not found in our record!')
        else:
            # If the form is invalid, display error messages
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)    
    
    context = {
        'form': form        
    }
    
    response = render(request, template, context=context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response

@login_required
def report_malicious(request): 
    """
    View function to report a malicious URL and deactivate associated short URLs.

    Parameters:
        request (HttpRequest): The HTTP request object that contains information about the request.

    Returns:
        HttpResponse: The HTTP response object that contains the rendered report_malicious.html template.
    """
    # Initialize site_info dictionary to store page's SEO meta information
    site = site_info()  
    site['title'] = 'Securely Report Malicious URLs | Protecting Your Online Safety'  
    site['description'] = 'Report malicious and suspicious URLs securely with our URL shortener. We use advanced encryption to safeguard your data. Help us create a safer online environment'  
    
    
    # Create a CheckingForm instance to handle the user's input data
    form = CheckingForm()        

                    
    
    context = {        
        'site_data': site, 
        'form': form                
    }
    response = render(request, 'selfurl/report_melicious.html', context=context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@login_required
def statistics(request):
    
    seo_info = site_info()  
    seo_info['title'] = 'Unlock Insights, Empower Decisions'
    seo_info['description'] = 'Gain valuable insights into your shortened URL performance. Our click tracking analytics provide comprehensive data to empower your decisions. Track clicks, locations, and more with ease. Discover the power of data-driven marketing.'
    
    seo_info['og_image'] = request.user.get_profile.avatar.url
    
    items = Shortener.objects.filter(creator = request.user).order_by('-created')   
    created_since = arrow.get((items.first()).created).humanize()     
    
    #Paginated response
    page = request.GET.get('page', 1)
    paginator = Paginator(items, 10)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)        
    
    context = {                
        'items' : items ,     
        'site_data' : seo_info ,

        'created_since' : created_since             
            }
    response =  render(request, 'selfurl/statistics.html', context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response



@login_required
def allreport(request, short_url):
    if request.user.is_paid or request.user.is_superuser:
        pass
    else:
        raise PermissionDenied
    
    reports = ReportMalicious.objects.filter(url__short_url = short_url).order_by('created')
    created_since = arrow.get((reports.first()).created).humanize()
    page = request.GET.get('page', 1)
    paginator = Paginator(reports, 10)
    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        reports = paginator.page(1)
    except EmptyPage:
        reports = paginator.page(paginator.num_pages)    
    
    seo_info = site_info() 
 
    
    context = {
        'short_url': short_url,
        'site_data' : seo_info ,
        'reports' : reports,
        'created_since' : created_since
            }
    
    
    response = render(request, 'selfurl/allreport.html', context=context)

    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@login_required
def generate_visitor_log_pdf(request, short_url):
    site_data = site_info()
    shortener = get_object_or_404(Shortener.objects.exclude(creator = None).prefetch_related('urlversion'), short_url=short_url)
    if is_reported(shortener.long_url):
        raise Http404  

    # Get the VisitorLog objects for the given Shortener
    visitor_logs = VisitorLog.objects.filter(shortener=shortener)

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="visitor_log_{short_url}.pdf"'
    response['Content-Meta'] = 'noindex, nofollow'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    # Create a PDF document
    
    ps = A4
    ph = ps[1]
    pw = ps[0]
    m = 0.5 * inch
    
    styles = getSampleStyleSheet()
    custom_heading_style = styles['Heading2'].clone(name='custom_heading_style', fontName='Helvetica-Bold', fontSize=18, alignment=1, textColor=colors.red)
    custom_normal_style = styles['Normal'].clone(name='custom_normal_style', fontName='Helvetica', fontSize=12, alignment=1)
    custom_normal_style_small = styles['Normal'].clone(name='custom_normal_style', fontName='Helvetica', fontSize=8, alignment=1, textColor=colors.blue)
    

    title = f'SELFURL--Statictics for URL {short_url}'
    author = f'{site_data.get("domain")}'
    creator = f'{site_data.get("domain")}'
    producer = f'{shortener.creator.email}'  
    
    doc = SimpleDocTemplate(
        response, 
        pagesize=ps, 
        leftMargin = m, 
        rightMargin = m,
        topMargin = m,
        bottomMargin = m,        
        )
    doc.title = title
    doc.author = author
    doc.creator = creator
    doc.producer = producer
    
    
    elements = [Spacer(1, 20)]
    elements.append(Paragraph(f': Statistics of {short_url} :', custom_heading_style)) 
   
    line_drawing = Drawing(pw-m-m-2,2)
    line = Line(0,0,pw-m-m-2,0)
    line_drawing.add(line)
    elements.append(line_drawing)  
    
    
    versions = shortener.urlversion.all()
    if versions.exists():
        elements.append(Paragraph(f'**Versions of the URL considered in this statistics: {", ".join(v.version for v in versions )}', custom_normal_style_small))      
    
    
    elements.append(Paragraph(f'URL created on top of: {shortener.long_url}', custom_normal_style))
    elements.append(Spacer(1, 20))
    
    style_table = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),  # Gray background for the header row
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for the header row
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Add padding to the header row
        ('GRID', (0, 0), (-1, -1), 1, '#AAAAAA'),  # Add borders to all cells
    ])
    
    # Set matplotlib backend to Agg
    matplotlib.use('Agg')    
    
 
    # Create a dictionary to store country-wise counts
    country_counts = {}    

    for vl in visitor_logs:
        secret_key = base64.b64decode(vl.logkey.key)
        cipher_suite = Fernet(secret_key)    
        decrypted_geodata = json.loads(cipher_suite.decrypt(vl.geo_data))        
        country = decrypted_geodata.get('country_name')        
        # Update the country count
        country_counts[country] = country_counts.get(country, 0) + 1        
        

    # Get the total clicked records count
    total_clicked = shortener.clicked
    center_x = pw / 2 - m*2
    # Create a custom Drawing to add the total clicked count circle
    total_clicked_drawing = Drawing(width=100, height=100)
    total_clicked_drawing.add(Circle(50, 50, 40, fill=1, stroke=0, strokeColor=None, fillColor='red'))  # Adjust the coordinates and colors as needed
    total_clicked_drawing.add(String(50, 50, str(total_clicked), fontSize=18, textAnchor='middle', fillColor='white'))
    # Calculate the X-coordinate to center the circle
    circle_x = center_x - total_clicked_drawing.width / 2
    # Move the Drawing to the center of the page horizontally
    total_clicked_drawing.translate(circle_x, 0)
    # Add the total clicked count circle to the elements list
    elements.append(Paragraph('Total Clicked Count:', styles['Heading4']))
    elements.append(Spacer(1, 10))  # Add some spacing between the heading and the circle

    elements.append(total_clicked_drawing)
    elements.append(Spacer(1, 20)) 


    # Create the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(list(country_counts.values()), labels=list(country_counts.keys()), autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # plt.title('Country-wise Visitor Statistics')

    # Save the chart to a buffer
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png')
    plt.close()

    # Reset the buffer's position to the beginning
    chart_buffer.seek(0)

    # Add the pie chart image to the PDF report
    elements.append(Paragraph('Country-wise Visitor Statistics:', styles['Heading4']))
    elements.append(Image(chart_buffer, width=300, height=300))
    elements.append(Spacer(1, 20))  # Add some spacing between the pie chart and the table

    # Create the table
    data = [['User Agent', 'Country', 'Clicked Date']]
    for vl in visitor_logs:
        secret_key = base64.b64decode(vl.logkey.key)
        cipher_suite = Fernet(secret_key)   
        decrypted_user_agent = json.loads(cipher_suite.decrypt(vl.user_agent))         
        decrypted_geodata = json.loads(cipher_suite.decrypt(vl.geo_data))   
     
        country = decrypted_geodata.get('country_name')        
        clicked_date = vl.visited # Assuming it's a UTF-8 encoded string        
        
        user_browser = str(decrypted_user_agent.get('user_browser')[0]) +'-'+ str(decrypted_user_agent.get('user_browser')[2])
        user_os = str(decrypted_user_agent.get('user_os')[0]) +'-'+ str(decrypted_user_agent.get('user_os')[2])
        user_device = str(decrypted_user_agent.get('user_device')[0]) +'-'+ str(decrypted_user_agent.get('user_device')[2])    

        # Add a row to the table
        data.append([
            f'{user_browser}/{user_os}/{user_device}',
            country,          
            str(clicked_date),
        ])

    table = Table(data)
    table.setStyle(style_table)

    # Add the table to the elements list
    elements.append(Paragraph('Visitor Log Table:', custom_heading_style))
    elements.append(table)    

    # Build the PDF document
    doc.build(
        elements,
        onFirstPage=header_footer,
        onLaterPages=header_footer,
        )
    return response

# Custom function to draw header and footer
def header_footer(canvas, doc):
    ps = A4
    ph = ps[1]
    pw = ps[0]
    m = 0.5 * inch
    site_data = site_info()
    # Header
    canvas.saveState()
    canvas.drawImage('http://' + site_data.get('domain') + site_data.get('logo'), m, ph-m, width=120, height=30)  
    canvas.drawString(m+120, ph-m, f"({site_data.get('domain')})")  
    canvas.line(m, ph-m-10, pw-m, ph-m-10)
    canvas.setFont('Helvetica', 10)
    canvas.drawString(m, ph-m-20, 'Service By: '+site_data.get('location'))  
    canvas.restoreState()

    # Footer
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.drawString(m, m, 'Generated on: {}'.format(timezone.now().strftime('%Y-%m-%d %H:%M:%S')))
    canvas.drawString(pw-m, m, 'Page %d' % doc.page)

    # Move to a new line for the next text
    canvas.drawString(m, m+10, 'This is an system generated report from encrypted data.')
    canvas.restoreState()
    
@login_required   
def generate_click_record_pdf_view(request, short_url):    
    shortener_obj = get_object_or_404(Shortener.objects.exclude(creator = None).prefetch_related('urlversion'), short_url=short_url)
    if is_reported(shortener_obj.long_url):
        raise Http404  
    pdf_response = generate_click_record_pdf(request, shortener_obj)
    return pdf_response
@login_required
def generate_click_record_pdf(request, shortener_obj):
    site_data = site_info()
    # Create a buffer to store the PDF
    buffer = io.BytesIO()
    ps = A4
    ph = ps[1]
    pw = ps[0]
    m = 0.5 * inch
    
    title = f'SELFURL -- Click record of the {shortener_obj.short_url}'
    author = f'{site_data.get("domain")}'
    creator = f'{site_data.get("domain")}'
    producer = f'{shortener_obj.creator.email}'  

    # Create a new PDF document with portrait orientation and letter page size
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=ps,
        leftMargin = m, 
        rightMargin = m,
        topMargin = m,
        bottomMargin = m )
    
    doc.title = title
    doc.author = author
    doc.creator = creator
    doc.producer = producer
    

    # Set up the styles for the document
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], alignment=TA_CENTER)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Gray background for table header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # White text for table header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for table header
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Light beige background for table content
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Initialize elements list to store content for the PDF
    elements = []


    # Spacer
    elements.append(Spacer(1, 12))
    elements.append(Spacer(1, 12))
    elements.append(Spacer(1, 12))
    

    # Report tagline and Shortener details
    elements.append(Paragraph(f'Click record of the {shortener_obj.short_url}', header_style))
    elements.append(Paragraph(f'Shortener Created from: {shortener_obj.long_url}', styles['Normal']))

    # Spacer
    elements.append(Spacer(1, 12))

 
    # Spacer
    elements.append(Spacer(1, 12))

    # Table tagline and intro text
    elements.append(Paragraph('-:Records:-', header_style))
    elements.append(Paragraph(f'First row represents the main URL, and the value in the "Clicked" column corresponds to the cumulative clicks across all versions. This inclusive count combines clicks from all versions of the {shortener_obj.short_url}, making it easier to understand the overall performance.', styles['Normal']))
    # Spacer
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f'Subsequent rows in the table display clicks for each individual version of the {shortener_obj.short_url}, allowing you to identify the clicks specific to each version, facilitating a comprehensive analysis of user engagement.', styles['Normal']))

    # Spacer
    elements.append(Spacer(1, 12))

    # Create a list to store table data
    table_data = [['Version', 'Clicked', 'Created At', 'Remarks']]
    table_data.append([shortener_obj.short_url, shortener_obj.clicked, shortener_obj.created.strftime('%Y-%m-%d'), 'Clicked mentioned here total including all version'])
    versions = shortener_obj.urlversion.all()
    for version in versions:
        table_data.append([version.version, version.clicked, version.created.strftime('%Y-%m-%d'), ''])

    # Create the table
    table = Table(table_data)
    table.setStyle(table_style)
    elements.append(table)

    # Spacer
    elements.append(Spacer(1, 12))

 

    # Build the PDF document
    doc.build(
        elements,
        onFirstPage=header_footer,
        onLaterPages=header_footer
        )

    # Get the value of the buffer and create an HTTP response with PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="click_record_{shortener_obj.short_url}.pdf"'
    response['Content-Meta'] = 'noindex'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    response.write(buffer.getvalue())
    buffer.close()

    return response






 
