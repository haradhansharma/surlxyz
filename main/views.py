from django.shortcuts import render
from django.urls import reverse
from main.context_processor import site_info
from django.templatetags.static import static
from django.http import JsonResponse

from selfurl.forms import (
    ShortenerForm,
)
from cms.models import (
    Page
)
from main.helper import (
    get_blogs,
    get_about_us_link,
    get_front_text
    
)

def index(request):
    
    form = ShortenerForm()  
    site = site_info() 
    
    site['title'] = site.get('slogan')
    
    front_page_data = f'{Page.objects.get(slug="for-front-page").body}'  
   
    latest_news = get_blogs()[:3]
    
    about_us_link = get_about_us_link()    

    
    front_text = get_front_text()
    
           
    context = {
        'form': form,
        'site_data' : site ,     
        'latest_news' : latest_news,
        'about_us_link': about_us_link,
        'front_text' : front_text,
        'front_page_data' : front_page_data
    }
    
    response = render(request, 'main/index.html', context = context)
    response['X-Robots-Tag'] = 'index, follow'
    return response

def webmanifest(request):
    site = site_info()      
    icons = [
        {
      "src": site['og_image'],
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": site['og_image'],
      "sizes": "144x144",
      "type": "image/png"
    },
    ]    
    ic192 = {
        "src": site['og_image'],
        "sizes": "192x192",
        "type": "image/png"        
    }
    
    icons.append(ic192)   
    ic512 = {
        "src": site['og_image'],
        "sizes": "512x512",
        "type": "image/png"        
    }
    icons.append(ic512)    
    data = {
        'name' : site['name'],
        'short_name' : site['name'],
        'icons' : icons,
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "display": "standalone"        
    }
    
    return JsonResponse(data, safe=False)

def webmanifest(request):
    site = site_info()  # Make sure this function provides the required site information safely

    icons = []
    # Add 192x192 icon
    ic192 = {
        "src": site['og_image'],  # Provide the URL to the 192x192 icon image
        "sizes": "192x192",
        "type": "image/png"
    }
    icons.append(ic192)

    # Add 512x512 icon
    ic512 = {
        "src": site['og_image'],  # Provide the URL to the 512x512 icon image
        "sizes": "512x512",
        "type": "image/png"
    }
    icons.append(ic512)

    # Construct the data for the manifest
    data = {
        'name': site['name'],  # Provide the name of your web app
        'short_name': 'selfurl',  # Provide a short name for your web app
        'description' : site['description'],
        'icons': icons,
        "lang": "en",
        "dir": "ltr",
        "categories": ["Internet", "Tools", 'Short URL'],
        "orientation": "portrait",
        "theme_color": "#21409A",  # Set the theme color of your web app
        "background_color": "#21409A",  # Set the background color of your web app
        "display": "standalone",  # Define how your web app should be displayed (e.g., standalone, fullscreen)
        "display_override": ["window", "fullscreen", "standalone"],
        "start_url": reverse('main:home'),  # Define the start URL of your web app (replace 'home' with the appropriate URL name)
        "scope": "/",  # Define the scope of your web app
        "permissions": ["geolocation", "notifications"]
        # Add more properties as needed based on your PWA requirements
    }

    return JsonResponse(data, safe=False)
