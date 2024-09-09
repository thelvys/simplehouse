from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Barber, Client, BarberProfile, ClientProfile

class BarberProfileInline(admin.StackedInline):
    model = BarberProfile
    can_delete = False
    verbose_name_plural = _('Barber Profile')

class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    verbose_name_plural = _('Client Profile')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_barber', 'is_client')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_barber', 'is_client')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User type'), {'fields': ('is_barber', 'is_client')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_barber', 'is_client'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'get_email', 'phone_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_number')
    ordering = ('user__username',)
    inlines = (BarberProfileInline,)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Full Name')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = _('Email')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'get_email', 'phone_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_number')
    ordering = ('user__username',)
    inlines = (ClientProfileInline,)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Full Name')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = _('Email')

@admin.register(BarberProfile)
class BarberProfileAdmin(admin.ModelAdmin):
    list_display = ('barber', 'specialization', 'years_of_experience')
    list_filter = ('specialization',)
    search_fields = ('barber__user__username', 'barber__user__first_name', 'barber__user__last_name', 'specialization')
    ordering = ('barber__user__username',)

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('client', 'preferred_style', 'loyalty_points')
    list_filter = ('preferred_style',)
    search_fields = ('client__user__username', 'client__user__first_name', 'client__user__last_name', 'preferred_style')
    ordering = ('client__user__username',)

# Optionally, you can customize the admin site header and title
admin.site.site_header = _("Saloon Accounts Administration")
admin.site.site_title = _("Saloon Accounts Admin Portal")
admin.site.index_title = _("Welcome to Saloon Accounts Admin Portal")
