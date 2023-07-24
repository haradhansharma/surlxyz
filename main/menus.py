
from django.urls import reverse
from main.helper import (
    pages,
    categories,
    model_with_field,
    has_threads

)
from django.core.cache import cache





def category_menus(request):
    all_cat = categories().filter(add_to_cat_menu = True, sites__id = request.site.id) 
    menu_items = []
    for cat in all_cat:
        if cat.have_items:         
            item_dict = {
                'title' : cat.title,
                'url' : cat.get_absolute_url(),
                'data_set': False,
                'icon' : cat.icon                
            }
            menu_items.append(item_dict)        
    return menu_items

def page_menus(request):    
    menu_items = cache.get('sh_page_menu_items')
    if menu_items is not None:
        return menu_items
    
    all_page = pages().filter(add_to_page_menu = True, sites__id = request.site.id)     
    menu_items = []
    for p in all_page:
        item_dict = {
            'title' : p.title,
            'url' : p.get_absolute_url(), 
            'data_set': False  
        }
        menu_items.append(item_dict)    
        
    item_dict = {
        'title' : 'Statistics',
        'url' : reverse('selfurl:statistics'), 
        'data_set': False  
    }
    menu_items.append(item_dict)    
    
    item_dict1 = {
        'title' : 'Report Malicious',
        'url' : reverse('selfurl:report_malicious'), 
        'data_set': False  
    }
    menu_items.append(item_dict1)    
    
    
        
    
    cache.set('sh_page_menu_items', menu_items, timeout=60 * 60)
        
    return menu_items




def footer_menu(request):
    
    menu_items = cache.get('sh_footer_menu_items')
    if menu_items is not None:
        return menu_items   
    
    
    objects_with_footer_menu = []
    for model in model_with_field('add_to_footer_menu'):
        objects_with_footer_menu += model.objects.filter(add_to_footer_menu=True, sites__id = request.site.id).order_by('title')      
          
    menu_items = []     
    
    
    for obj in objects_with_footer_menu:
        item_dict = {
            'title' : obj.title,
            'url' : obj.get_absolute_url(),  
            'data_set': False 
        }
        menu_items.append(item_dict)      
        
        
    menu_items.append(
        {'title': 'Blog', 'url': reverse('cms:latest_blogs'), 'data_set': False},        
        ) 
    
    menu_items.append(
        {'title': 'Contact Us', 'url': reverse('contact:contact'), 'data_set': False},        
        )    

    
    cache.set('sh_footer_menu_items', menu_items, timeout=60 * 60)
    
        
    return menu_items

def header_menu(request):    
    menu_items = cache.get('sh_header_menu_items')
    if menu_items is not None:
        return menu_items   
    
    objects_with_header_menu = []

    for model in model_with_field('add_to_header_menu'):     
        objects_with_header_menu += model.objects.filter(add_to_header_menu=True, sites__id = request.site.id).order_by('title')
        
    menu_items = [] 
    menu_items.append(
        {'title': 'Home', 'url': '/', 'data_set': False},        
        )     
    
    menu_items.append(
        {'title': 'Actions', 'url': False, 'data_set': page_menus(request) },        
        ) 
    
    for obj in objects_with_header_menu:
        have_items = getattr(obj, 'have_items', None)
        if (have_items and obj.have_items) or obj.add_to_header_menu:
            item_dict = {
                'title': obj.title,
                'url': obj.get_absolute_url(),
                'data_set': False
            }
            menu_items.append(item_dict)
            
    menu_items.append(
        {'title': 'Blogs', 'url': reverse('cms:latest_blogs'), 'data_set': False},        
        )    
    
    menu_items.append(
        {'title': 'Contact', 'url': reverse('contact:contact'), 'data_set': False},        
        ) 
    
    cache.set('sh_header_menu_items', menu_items, timeout=60 * 60)
        
    return menu_items


def user_menu(request):   
        
    menu_items = []     
    submenus = []   
    
    if request.user.is_authenticated:        
        item_dict = {
            'title' : 'Profile Settings',
            'url' : reverse('accounts:profile_setting', args=[request.user.id]), 
            'data_set': False  
        }
        submenus.append(item_dict)        
        item_dict2 = {
            'title' : 'Change Password',
            'url' : reverse('accounts:change_pass'), 
            'data_set': False  
        }
        submenus.append(item_dict2)        
        item_dict3 = {
            'title' : 'Logout',
            'url' : reverse('logout'), 
            'data_set': False  
        }
        submenus.append(item_dict3)   
        
        if has_threads(request.user.email):
            item_dict4 = {
                'title' : 'Contact Threads',
                'url' : reverse('contact:threads', args=[str(request.user.email)]), 
                'data_set': False  
            }
            submenus.append(item_dict4)   
        
        
              
        menu_items.append(
            {'title': f'{request.user.username}', 'url': False, 'data_set': submenus},        
            )    
    else:
        item_dict = {
            'title' : 'Login',
            'url' : reverse('login'), 
            'data_set': False  
        }
        submenus.append(item_dict)        
        item_dict2 = {
            'title' : 'SignUp',
            'url' : reverse('accounts:signup'), 
            'data_set': False  
        }
        submenus.append(item_dict2)        
        menu_items.append(
            {'title': f'Accounts', 'url': False, 'data_set': submenus},        
            )      
    return menu_items




    



    