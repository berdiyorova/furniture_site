from django.contrib import admin

from users.models import UserModel


@admin.register(UserModel)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('is_active',)
