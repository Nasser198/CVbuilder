from django.contrib import admin

from coreapp.models import WebsiteActions

# Register your models here.

class AdminWebsiteActions(admin.ModelAdmin):
    list_display = ['name', 'counter']

admin.site.register(WebsiteActions, AdminWebsiteActions)