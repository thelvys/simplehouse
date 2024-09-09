''' Common models for the project '''

from django.db import models
from django.utils.translation import gettext_lazy as _

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified at"), auto_now=True)

    class Meta:
        abstract = True

class Currency(TimestampMixin):
    code = models.CharField(_("Code"), max_length=3, unique=True)
    name = models.CharField(_("Name"), max_length=50, unique=True)
    is_default = models.BooleanField(_("Is default"), default=False)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @classmethod
    def get_default(cls):
        return cls.objects.get_or_create(
            code='USD',
            defaults={'name': _('US Dollar'), 'is_default': True}
        )[0]
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Currency.objects.filter(salon=self.salon, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        unique_together = ['code', 'salon']

class Attachment(TimestampMixin):
    file = models.FileField(_("File"), upload_to="attachments/")
    description = models.CharField(_("Description"), max_length=255)

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")