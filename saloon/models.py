''' Models for the saloon app '''

from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from commonapp.models import TimestampMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Salon(MPTTModel, TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_("Parent salon"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salons', verbose_name=_("Owner"))
    is_active = models.BooleanField(_("Is active"), default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Salon")
        verbose_name_plural = _("Salons")

    def __str__(self):
        return self.name

    def get_active_barbers(self):
        return self.barbers.filter(is_active=True)

class SalonPermission(TimestampMixin):
    PERMISSION_CHOICES = [
        ('can_manage', _('Can manage salon')),
        ('can_read', _('Can read salon data')),
        ('can_manage_finance', _('Can manage finance')),
        ('can_manage_inventory', _('Can manage inventory')),
        ('can_manage_shave', _('Can manage shave')),
        ('can_manage_hairstyle', _('Can manage hairstyle')),
        ('can_manage_barbers', _('Can manage barbers')),
    ]

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon_permissions')
    permission_type = models.CharField(_('permission type'), max_length=50, choices=PERMISSION_CHOICES)

    class Meta:
        unique_together = ('salon', 'user', 'permission_type')
        verbose_name = _("Salon Permission")
        verbose_name_plural = _("Salon Permissions")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.salon.name} - {self.get_permission_type_display()}"

class BarberType(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.name

class Barber(TimestampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='barbers', verbose_name=_("Salon"))
    barber_type = models.ForeignKey(BarberType, on_delete=models.CASCADE, verbose_name=_("barber type"))
    contract = models.FileField(_("Contract"), upload_to="contracts/", null=True, blank=True)
    phone = models.CharField(_("Phone"), max_length=255, null=True, blank=True)
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"), null=True, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = _('Barber')
        verbose_name_plural = _('Barbers')

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("Start date must be before end date."))
        
        overlapping = Barber.objects.filter(
            salon=self.salon,
            start_date__lte=self.end_date or timezone.now().date(),
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError(_("This assignment overlaps with an existing one."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today and (not self.end_date or self.end_date >= today)

class Client(TimestampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients', verbose_name=_("Preferred Salon"))
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    phone = models.CharField(_("Phone"), max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")