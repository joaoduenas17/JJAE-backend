from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from .models import  User

class UserAdmin(SimpleHistoryAdmin):
    list_display = ('id','email', 'name', 'last_name', 'photo',  'created_at', )
    list_filter = ('name', 'last_name', )
    history_list_display = ["email"]
    search_fields = ('email', 'rol',)


admin.site.register(User, UserAdmin )




