from django.contrib import admin

from . models import *

admin.site.register(Shortener)
admin.site.register(Versions)
admin.site.register(ReportMalicious)



