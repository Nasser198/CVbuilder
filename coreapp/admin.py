# from django.contrib import admin

# from coreapp.models import WebsiteActions

# Register your models here.
from django.contrib import admin
from .models import UserInformation, WebsiteActions
from coreapp.models import UserIP
import requests

class UserInformationAdmin(admin.ModelAdmin):
    list_display = ('email', 'request_count', 'request_sum', 'country')
    readonly_fields = ('request_count', 'request_sum')

class WebsiteActionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'counter', 'timestamp')

class UserIPAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'country', 'time')
    
    def save_model(self, request, obj, form, change):
        # Use the ipapi.co API to retrieve the country name associated with the IP address
        response = requests.get('https://ipapi.co/{}/country_name/'.format(obj.ip_address))
        if response.status_code == 200:
            obj.country = response.text
        else:
            obj.country = None
        obj.save()

admin.site.register(UserInformation, UserInformationAdmin)
admin.site.register(WebsiteActions, WebsiteActionsAdmin)
admin.site.register(UserIP, UserIPAdmin)




    

# class AdminWebsiteActions(admin.ModelAdmin):
#     list_display = ['name', 'counter']

# admin.site.register(WebsiteActions, AdminWebsiteActions)

