from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Item, UserProfile, Notification

# Inline so UserProfile appears directly inside the User detail page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('full_name', 'department', 'role')

# Extend the default User admin to include the inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register User with our extended admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'department', 'role')
    list_filter = ('role',)
    search_fields = ('full_name', 'department', 'user__username', 'user__email')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'item_name', 'location', 'reporter', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('item_name', 'location', 'description')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
