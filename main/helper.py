
from datetime import datetime
from django.conf import settings
from django.core.mail import get_connection
from django.apps import apps
# from .models import Page, Blog, Category, ResponseBackup
from django.core.cache import cache
from django.db.models import Count, Q
import random
import string
from django.db.models.functions import TruncMonth, TruncYear
from cms.models import (
    Category,
    Page,
    Blog,
    Action
)
from config.settings import MONTH_IN_SECONDS, VT_RATE_LIMITE_PER_MONTH
from selfurl.models import ReportMalicious, Shortener
from django.utils import timezone

def timestamp_to_datetime(unix_timestamp):
    # Convert Unix timestamp to a datetime object in the Django settings timezone
    return timezone.make_aware(datetime.fromtimestamp(unix_timestamp), timezone.get_current_timezone())


def get_sleep_time_for_vt_check():
    current_time = timezone.now().timestamp()

    # Get the last request time from the cache
    last_request_time = cache.get("su_last_request_time", 0)

    # Calculate the time elapsed since the last request
    time_elapsed = current_time - last_request_time

    # Calculate the number of requests allowed in the elapsed time
    requests_allowed = (time_elapsed / MONTH_IN_SECONDS) * VT_RATE_LIMITE_PER_MONTH

    if requests_allowed >= 1:
        # Update the last request time to the current time
        cache.set("su_last_request_time", current_time, MONTH_IN_SECONDS)
        return 0  # No need to sleep, request can be made immediately

    # Calculate the time to wait before making the next request
    time_to_wait = (1 - requests_allowed) * (MONTH_IN_SECONDS / VT_RATE_LIMITE_PER_MONTH)

    return time_to_wait

'''helper function'''
def random_digits():
    return "%0.3d" % random.randint(0, 99)

'''helper function'''
def check_exists(short_url):
    #make unique
    try:
        data = Shortener.objects.get(short_url = short_url)
        while data.short_url == short_url:
            return str(short_url) + str(random_digits())
    except:
        return short_url
    
def report_que(long_url):
    """
    Checks if the given long URL has been reported as malicious.

    Args:
        long_url (str): The long URL to check.

    Returns:
        bool: True if the long URL has been reported, False otherwise.
    """

    # Use the `filter()` method to get all the `ReportMalicious` objects
    # where the `url` field has a `long_url` value that matches the given long URL.
    # Then, use the `Count()` aggregate function to count the number of objects
    # that were returned.
    
    reported_count = ReportMalicious.objects.filter(url__long_url=long_url).exclude(check_decision = settings.CLEAN_DECISION).aggregate(Count('id'))['id__count']
    
    return reported_count

def is_reported(long_url):
    
    reported_count = report_que(long_url)

    # If the count is greater than 0, then the long URL has been reported.

    return reported_count > 0


def get_blog_archive():

    blog_archives = cache.get('su_blog_archives')
    if blog_archives is not None:
        return blog_archives

    blog_archives = Blog.published.annotate(
            month=TruncMonth('updated_at')                     
        ).values('month').annotate(total_blogs=Count('id')).order_by('-month')    
    
    cache.set('su_blog_archives', blog_archives, timeout=60 * 60) 
    return blog_archives




def get_top_views():

    top_views_blog = cache.get('su_top_views_blog')
    if top_views_blog is not None:
        return top_views_blog

    top_views_blog = Blog.published.annotate(
        total_view_count=Count('actions', filter=Q(actions__action_type=Action.VIEW))
    ).order_by('-total_view_count')[:6]  
    
    cache.set('su_top_views_blog', top_views_blog, timeout=60 * 60) 
    return top_views_blog

def get_category_with_count():

    category_count = cache.get('su_category_count')
    if category_count is not None:
        return category_count

    category_count = Category.objects.prefetch_related('blogs_category').annotate(blog_count=Count('blogs_category', filter=Q(blogs_category__status='published')))    
    
    cache.set('su_category_count', category_count, timeout=60 * 60) 
    return category_count



def get_blogs():

    blogs = cache.get('su_blogs')
    if blogs is not None:
        return blogs


    blogs = Blog.published.all()
    cache.set('su_blogs', blogs, timeout=60 * 60) 
    return blogs

def categories():
    categories = cache.get('su_categories')
    if categories is not None:
        return categories
    categories = Category.objects.filter(is_active = True)
    cache.set('su_categories', categories, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return categories


def pages():
    pages = cache.get('su_pages')
    if pages is not None:
        return pages
    pages = Page.objects.filter(is_active = True, status='published') 
    cache.set('su_pages', pages, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return pages

def get_consent_pages():
    pages = cache.get('su_consent_pages')
    if pages is not None:
        return pages
    pages = Page.objects.filter(is_active = True, consent_required=True) 
    cache.set('su_consent_pages', pages, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return pages

def get_about_us_link():
    about_us_link = cache.get('su_about_us_link')
    if about_us_link is not None:
        return about_us_link
    about_us_link = Page.objects.get(slug = 'about-us').get_absolute_url
    cache.set('su_about_us_link', about_us_link, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return about_us_link

def get_front_text():
    front_text = cache.get('su_front_text')
    if front_text is not None:
        return front_text
    front_text = Page.objects.get(slug = 'for-front-page').body
    cache.set('su_front_text', front_text, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return front_text  



def model_with_field(field_name):    
    models_with_field_name = []
    # Iterate over all installed apps
    for app_config in apps.get_app_configs():
        # Get all models for the current app
        for model in app_config.get_models():
            # Check if the model has a field named 'field_name'
            if hasattr(model, field_name):
                models_with_field_name.append(model)
    return models_with_field_name

# Imported for backwards compatibility and for the sake
# of a cleaner namespace. These symbols used to be in
# django/core/mail.py before the introduction of email
# backends and the subsequent reorganization (See #10355)
from django.core.mail.message import (
    
    EmailMultiAlternatives,
    EmailMessage,

) 

def custom_send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
    html_message=None,
    cc=None,
    reply_to=None,
    bcc=None,
):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(
        subject, message, from_email, recipient_list, cc=cc, reply_to = reply_to, bcc=bcc, connection=connection
    )
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    return mail.send()

def custom_send_mass_mail(
    datatuple, fail_silently=False, auth_user=None, auth_password=None, connection=None
):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), send
    each message to each recipient list. Return the number of emails sent.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    messages = [
        EmailMessage(subject, message, sender, recipient, cc=cc, reply_to=reply_to, bcc=bcc, connection=connection)
        for subject, message, sender, recipient, cc, reply_to, bcc in datatuple
    ]
    return connection.send_messages(messages)
from contact.models import ContactMessage
def has_threads(email):    
    thread_count = ContactMessage.objects.filter(email = email).count()
    return thread_count > 0

