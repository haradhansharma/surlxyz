import re
from django.conf import settings
from .models import ExSite    
from django.contrib.sites.models import Site
from django.core.cache import cache
from .models import *
from .menus import (
    category_menus,
    page_menus,
    footer_menu,
    header_menu,
    user_menu,

)
from .helper import get_consent_pages


def site_info():
    """
    Retrieve site-wide information and cache it for optimized performance.

    This function retrieves various site-wide information and stores it in the cache to reduce database queries.
    It first attempts to fetch the site data from the cache. If available, it returns the cached data immediately.
    If the data is not found in the cache, it retrieves the information from the database, creates a related ExSite
    object if necessary, and stores the data in the cache for future use.

    Returns:
        dict: A dictionary containing site-wide information such as name, domain, description, author, meta tags,
              favicon URL, mask icon URL, logo URL, trademark, slogan, Open Graph image URL, social media links,
              email, location, and phone number.

    """
    # Attempt to retrieve site data from the cache
    data = cache.get('site_data')

    if data is not None:
        return data

    # Assuming you have a Site object
    site = Site.objects.get()

    try:
        # Retrieve the related ExSite object if it exists
        extend = site.extend
    except ExSite.DoesNotExist:
        # Create a related ExSite object if it does not exist
        extend = ExSite(site=site)
        extend.save()

    # Prepare a dictionary containing various site-wide information
    data = {
        'name': extend.site.name,
        'domain': extend.site.domain,
        'description': extend.site_description,
        'author': 'SINCEHENCE LTD',
        'meta_tag': extend.site_meta_tag,
        'favicon': extend.site_favicon.url if extend.site_favicon else '',
        'mask_icon': extend.mask_icon.url if extend.mask_icon else '',
        'logo': extend.site_logo.url if extend.site_logo else '',
        'trademark': extend.trademark,
        'slogan': extend.slogan,
        'og_image': extend.og_image.url if extend.og_image else '',
        'facebook_link': extend.facebook_link,
        'twitter_link': extend.twitter_link,
        'linkedin_link': extend.linkedin_link,
        'instagram_link': extend.instagram_link,
        'email': extend.email,
        'location': extend.location,
        'phone': extend.phone,
    }

    # Store the site data in the cache with a timeout of 3600 seconds (1 hour)
    cache.set('su_site_data', data, timeout=3600)

    return data


def str_list_frm_path(request):   
    path = request.path

    # Split the path at each special character using a regular expression
    path_segments = re.split(r'[-_&/]', path)

    # Remove any empty strings from the list of path segments
    path_segments = [s for s in path_segments if s]
    return path_segments


def check_consent(request, consent_urls):
    """
    Check if user has given consent to access the current page.

    This function checks whether the user has given consent to access the current page.
    If 'consent_given' is not present in the session, it sets it to 'False'.
    If the user has given consent or the current page is in the list of consent_urls, it returns True.
    Otherwise, it returns False.

    Parameters:
        request (HttpRequest): The incoming request object containing user information and session data.
        consent_urls (list): A list of URLs that require user consent.

    Returns:
        bool: True if consent is given or the current page requires consent; False otherwise.

    """
    if 'concent_given' not in request.session:
        request.session['concent_given'] = 'False'

    if request.session.get('concent_given') == 'True':
        consent_given = True
    elif request.path in consent_urls:
        consent_given = True
    else:
        consent_given = False

    return consent_given 



def core_con(request):
    """
    Custom context processor to provide common data and check user consent.

    This context processor is responsible for providing common data to templates and checking user consent.
    It retrieves the list of URLs that require consent and checks if the user has given consent for the current page.
    The context dictionary includes 'consent_given' to indicate the user's consent status.

    Parameters:
        request (HttpRequest): The incoming request object containing user information and session data.

    Returns:
        dict: A dictionary containing common data and the 'consent_given' status.

    """
    consent_pages = get_consent_pages()
    consent_urls = []

    for cp in consent_pages:
        consent_urls.append(cp.get_absolute_url())

    # Check user consent using the check_consent function.
    consent_given = check_consent(request, consent_urls)

    # Get additional site data from the site_info function.
    site_data = site_info()

    # Create the context dictionary with common data and consent status.
    context = {
        'consent_given': consent_given,
        'category_menus': category_menus(request),
        'page_menus': page_menus(request),
        'footer_menu': footer_menu(request),
        'header_menu': header_menu(request),
        'user_menu': user_menu(request),
        'site_data': site_data,
        'consent_pages': consent_pages,
    }

    return context