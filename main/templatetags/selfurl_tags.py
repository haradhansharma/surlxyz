import base64
from django import template
from django.db.models import Count, Q

from selfurl.models import ReportMalicious
from main.helper import is_reported as reported_url, report_que as in_que

register = template.Library()

@register.filter
def is_reported(long_url):
    return reported_url(long_url)

@register.filter
def report_que(long_url):
    return in_que(long_url)

@register.filter
def base64_encode(email):
    return base64.b64encode(email.encode('utf-8')).decode('utf-8')

@register.filter
def base64_decode(encoded_email):
    return base64.b64decode(encoded_email.encode('utf-8')).decode('utf-8')