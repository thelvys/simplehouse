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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Salon")
        verbose_name_plural = _("Salons")

    def get_active_assignments(self):
        return self.salonassignment_set.filter(is_active=True, end_date__gte=timezone.now().date())

    def get_assigned_barbers(self):
        return [assignment.barber for assignment in self.get_active_assignments()]

class SalonAssignment(TimestampMixin):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, verbose_name=_("Salon"))
    barber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Barber"))
    contract = models.FileField(_("Contract"), upload_to="contracts/", null=True, blank=True)
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    is_active = models.BooleanField(_("Is active"), default=True)

    def __str__(self):
        return f"{self.barber.get_full_name()} - {self.salon.name}"
    
    class Meta:
        verbose_name = _("Salon assignment")
        verbose_name_plural = _("Salon assignments")
        unique_together = [('salon', 'barber', 'start_date')]

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("Start date must be before end date."))
        
        overlapping = SalonAssignment.objects.filter(
            salon=self.salon,
            barber=self.barber,
            start_date__lte=self.end_date,
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
        return self.is_active and self.start_date <= today <= self.end_date