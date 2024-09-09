''' Models for the accounts app '''

from django.db import models
from django.utils import timezone 
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from commonapp.models import TimestampMixin, Attachment

from config import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Enter email.")
        
        user = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255, blank=False)
    first_name = models.CharField(max_length=90, blank=False)  # Ajout de first_name
    last_name = models.CharField(max_length=90, blank=False)   # Ajout de last_name
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class BarberType(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.name

class Barber(TimestampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    barber_type = models.ForeignKey(BarberType, on_delete=models.CASCADE, verbose_name=_("barber type"))
    address = models.CharField(_("Address"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=255)

    def __str__(self):
        return self.user.full_name

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = _('Barber')
        verbose_name_plural = _('Barbers')
        
class Client(TimestampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    phone = models.CharField(_("Phone"), max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")