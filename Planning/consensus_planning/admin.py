from django.contrib import admin
from . models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
# Register your models here.
'''

class AccountAdmin(UserAdmin):
    list_display=['email','username','date_joined','last_login','is_admin','is_staff']
    search_fileds=('email','username')
    readonly_filed=('id','date_joined','last_login')
    filter_horizontal=()
    list_filter=()
    fieldsets=()

admin.site.register(Account,AccountAdmin)
'''
class CustomGroupAdmin(admin.ModelAdmin):
    # Custom configurations for the Group model (optional)
    list_display = ['name']  # List display for the Group admin page

admin.site.unregister(Group)  # Unregister the default admin for Group
admin.site.register(Group, CustomGroupAdmin)
