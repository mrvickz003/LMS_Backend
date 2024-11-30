from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.models import CustomUser, Form, FormData,FormFile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'photo', 'mobile_number', 'is_staff', 'is_active']  # Add 'photo' here
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Customizing fieldsets to include the 'photo' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'photo', 'mobile_number')}),  # Add 'photo' here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Add fields for creating a new user, including 'photo'
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'mobile_number', 'last_name', 'photo', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Form)
admin.site.register(FormData)
admin.site.register(FormFile)
