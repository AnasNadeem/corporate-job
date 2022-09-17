from django.contrib import admin
from jobapp.models import (Corporate,
                           Job,
                           Profile,
                           User,
                           )


class TimeBaseModelAdmin(admin.ModelAdmin):
    list_display = ("created_at", "updated_at")


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name")
    search_fields = ["email", "first_name", "last_name"]


class CorporateAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "location") + TimeBaseModelAdmin.list_display
    search_fields = ["user", "name"]


class JobAdmin(admin.ModelAdmin):
    list_display = ("corporate", "title", "total_interest") + TimeBaseModelAdmin.list_display
    search_fields = ["corporate", "title"]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_paid",) + TimeBaseModelAdmin.list_display


admin.site.register(User, UserAdmin)
admin.site.register(Corporate, CorporateAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Profile, ProfileAdmin)
