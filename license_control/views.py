from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from license_control.models import Licences

def lc(request):
    license = Licences.objects.all()    
    context = dict()    
    for l in license:
        if l.validaty > timezone.now():
            context.update({
                l.party_domain : False
            })
        else:
            context.update({
                l.party_domain : True
            })
    return JsonResponse(context)
