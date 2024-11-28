from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Habit, HabitCompletion

class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the CustomUser model
    """
    model = CustomUser
    
    # The fields to be used in displaying the User model
    list_display = (
        'email', 
        'is_staff', 
        'is_active', 
        'created_at'
    )
    
    list_filter = (
        'is_staff', 
        'is_active'
    )
    
    # Fieldsets for the user edit page in admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('avatar',)}),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ['last_login']}),
    )
    
    # Fieldsets for creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            )
        }),
    )
    
    # Use email as the search and ordering fields
    search_fields = ('email',)
    ordering = ('email',)

# Register the CustomUser model with the custom admin configuration
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Habit model
    """
    list_display = (
        'name', 
        'user', 
        'frequency', 
        'start_date', 
        'end_date', 
        'created_at'
    )
    
    list_filter = (
        'frequency', 
        'start_date', 
        'end_date',
        'user'
    )
    
    search_fields = (
        'name', 
        'description', 
        'user__email'
    )
    
    readonly_fields = (
        'id', 
        'created_at', 
        'updated_at'
    )
    
    fieldsets = (
        (None, {
            'fields': (
                'id', 
                'user', 
                'name', 
                'description'
            )
        }),
        ('Habit Details', {
            'fields': (
                'frequency', 
                'start_date', 
                'end_date'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            )
        })
    )
    
    ordering = ('-created_at',)

@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the HabitCompletion model
    """
    list_display = (
        'habit', 
        'date', 
        'status', 
        'created_at'
    )
    
    list_filter = (
        'status', 
        'date', 
        'habit__name',
        'habit__user'
    )
    
    search_fields = (
        'habit__name', 
        'habit__user__email'
    )
    
    readonly_fields = (
        'id', 
        'created_at', 
        'updated_at'
    )
    
    fieldsets = (
        (None, {
            'fields': (
                'id', 
                'habit', 
                'date', 
                'status'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            )
        })
    )
    
    ordering = ('-date',)