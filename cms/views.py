from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from main.context_processor import site_info
from django.utils.html import strip_tags
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from main.agent_helper import get_ip
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.views.generic.edit import CreateView
from django.db.models import Count, Q
from main.helper import (
    custom_send_mail, 
    custom_send_mass_mail, 
    get_blogs, 
    get_category_with_count,
    get_top_views,
    get_blog_archive
    )
from .models import *
from .forms import *
import calendar
from django.views.decorators.cache import cache_control

import logging
log =  logging.getLogger('log')


# Create your views here.


def get_3_parameter():
    categories = get_category_with_count()   
    
    top_views = get_top_views()    
    
    blog_archive =  get_blog_archive()
    
    return categories, top_views, blog_archive
    
    
def archive_detail(request, year, month):
    template_name = 'cms/category_details.html'  
    
    search_form = BlogSearchForm()
    if 'search_query' in request.GET:
        search_form = BlogSearchForm(request.GET)        
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']    
            blogs = Blog.published.filter(
                (Q(title__icontains=search_query) | Q(body__icontains=search_query)), updated_at__year=year, updated_at__month=month
            )          
    else:   
        blogs = Blog.published.filter(updated_at__year=year, updated_at__month=month)
    
         

    categories, top_views, blog_archive = get_3_parameter()

    paginator = Paginator(blogs, 10) 

    page_number = request.GET.get('page')
    
    try:
        blogs = paginator.page(page_number)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages) 
        
        
    site = site_info()
    site['title'] = f'Blog archive of {calendar.month_name[month]}, {year}'
    site['description'] = f'Discover a wealth of valuable insights, tips, and knowledge in our blog archive. Explore a wide range of topics, from tech trends to marketing strategies. Stay informed and inspired with our collection of informative blog posts.'
    
     
    context = {
        'search_form': search_form,
        'blogs': blogs,
        'site_data' : site,
        'categories' : categories,
        'top_views' : top_views,
        'blog_archive' : blog_archive,

    }
    
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'index, follow'
    return response 


@cache_control(no_cache=True, must_revalidate=True, no_store=True)   
def category_detail(request, slug):
    
    template_name = 'cms/category_details.html'  

    category = get_object_or_404(Category.objects.prefetch_related('blogs_category'), slug=slug)   
    search_form = BlogSearchForm()
    
    if 'search_query' in request.GET:
        search_form = BlogSearchForm(request.GET)        
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']    
            blogs = category.blogs_category.filter(
                (Q(title__icontains=search_query) | Q(body__icontains=search_query)),
                status = 'published'
            )          
    else:        
        blogs = category.blogs_category.filter(status = 'published')       
 
    
    categories, top_views, blog_archive = get_3_parameter()     
    

    paginator = Paginator(blogs, 10) 

    page_number = request.GET.get('page')
    
    try:
        blogs = paginator.page(page_number)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages) 
        
        
    site = site_info()
    site['title'] = f'Unlocking Knowledge, Category by {category.title}'  
    site['description'] = category.description
    
     
    context = {
        'search_form': search_form,
        'category' : category,
        'blogs': blogs,
        'site_data' : site,
        'categories' : categories,
        'top_views' : top_views,
        'blog_archive' : blog_archive
    }
    
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'index, follow'
    return response 

def user_blogs(request, username):
    
    template_name = 'cms/category_details.html'  
    
    search_form = BlogSearchForm()
    
    if 'search_query' in request.GET:
        search_form = BlogSearchForm(request.GET)        
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']    
            blogs = Blog.published.filter(
                (Q(title__icontains=search_query) | Q(body__icontains=search_query)), 
                creator__username = username
            )          
    else:
        blogs = Blog.published.filter(creator__username = username) 
 
    
    categories, top_views, blog_archive = get_3_parameter()     
    

    paginator = Paginator(blogs, 10) 

    page_number = request.GET.get('page')
    
    try:
        blogs = paginator.page(page_number)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages) 
        
        
    site = site_info()
    site['title'] = f'Latest Blogs of Creator: {username}'    
    site['description'] = f"Welcome to {username}'s blog, where you'll find a wealth of valuable insights and personal experiences. Explore a diverse range of topics, including {username}'s areas of expertise or interests, and gain unique perspectives on relevant industry or subject. Expand your knowledge and engage with thought-provoking content on {username}'s blog."
    
     
    context = {
        'search_form': search_form,
        'blogs': blogs,
        'site_data' : site,
        'categories' : categories,
        'top_views' : top_views,
        'blog_archive' : blog_archive
    }
    
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'index, follow'
    return response 


def latest_blogs(request):
    
    template_name = 'cms/category_details.html'
    
    search_form = BlogSearchForm()
    
    if 'search_query' in request.GET:
        search_form = BlogSearchForm(request.GET)        
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']
            blogs = Blog.published.filter(
                Q(title__icontains=search_query) | Q(body__icontains=search_query)
            )             
    else:
        blogs = get_blogs()
    
    categories, top_views, blog_archive = get_3_parameter()     
    

    paginator = Paginator(blogs, 10) 

    page_number = request.GET.get('page')
    
    try:
        blogs = paginator.page(page_number)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages) 
        
        
    site = site_info()
    site['title'] = f'Stay Updated with Our Latest Insights and Expert Blog Posts' 
    site['description'] = 'Explore our latest blog posts for valuable insights, expert tips, and industry trends. Stay informed with our informative and engaging content on various topics. Read now!'
    
     
    context = {
        'search_form': search_form,
        'blogs': blogs,
        'site_data' : site,
        'categories' : categories,
        'top_views' : top_views,
        'blog_archive' : blog_archive
    }
    
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'index, follow'
    return response 

def page_detail(request, slug):
    template_name = 'cms/page_detail.html'
    
    page = get_object_or_404(Page, slug=slug) 

    page.view(request)     
    
    site = site_info()
     
     
    #render {} wraped syntax from site dictionary
    rendered_body = page.body.format(**site)
    page.body = rendered_body
    
    banner = page.top_banenr.url if page.top_banenr else site.get('og_image')
    
    site['title'] = page.top_tagline
    site['description'] = page.meta_description
    site['og_image'] = banner
    
    
    
    
    context = {
        'page' : page,
        'site_data' : site
    }
    
    response = render(request, template_name, context=context)   
    response['X-Robots-Tag'] = 'index, follow'
    return response 


@cache_control(no_cache=True, must_revalidate=True, no_store=True)   
def blog_detail(request, slug):
    template_name = 'cms/blog_detail.html'
    
    blog = get_object_or_404(Blog.published.prefetch_related('categories'), slug=slug)   
     
    blog.view(request)    
 
        
    site = site_info()
    site['title'] = blog.title[:45]
    truncated_string = strip_tags(blog.body)[:160]
    site['description'] = truncated_string
    site['og_image'] = blog.feature.url
    
    
    context = {      
        'blog' : blog,   
        'site_data' : site,      
    }   
    
    response = render(request, template_name, context=context)
    response['X-Robots-Tag'] = 'index, follow'
    return response 

    



    