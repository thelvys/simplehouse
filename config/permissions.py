from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from saloon.models import Salon, SalonAssignment, SalonPermission

class BasePermissionMixin(UserPassesTestMixin):
    def handle_no_permission(self):
        raise PermissionDenied

class VisitorPermissionMixin(BasePermissionMixin):
    def test_func(self):
        return not (self.request.user.is_barber or self.request.user.is_salon_owner)

class SalonOwnerPermissionMixin(BasePermissionMixin):
    def test_func(self):
        salon_id = self.kwargs.get('pk') or self.kwargs.get('salon_id')
        return self.request.user.is_salon_owner and Salon.objects.filter(id=salon_id, owner=self.request.user).exists()

class BarberPermissionMixin(BasePermissionMixin):
    def test_func(self):
        salon_id = self.kwargs.get('pk') or self.kwargs.get('salon_id')
        return self.request.user.is_barber and SalonAssignment.objects.filter(
            barber=self.request.user, salon_id=salon_id, is_active=True
        ).exists()

class SalonSpecificPermissionMixin(BasePermissionMixin):
    permission_type = None

    def test_func(self):
        user = self.request.user
        salon_id = self.kwargs.get('pk') or self.kwargs.get('salon_id')
        
        if user.is_superuser or is_salon_owner(user, salon_id):
            return True
        
        return SalonPermission.objects.filter(
            salon_id=salon_id,
            user=user,
            permission_type=self.permission_type
        ).exists()

class CanManageSalonMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_manage'

class CanReadSalonMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_read'

class CanManageFinanceMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_manage_finance'

class CanManageInventoryMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_manage_inventory'

class CanManageShaveMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_manage_shave'

class CanManageHairStyleMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_manage_hairstyle'

class CanManageBarbersMixin(SalonSpecificPermissionMixin):
    permission_type = 'can_manage_barbers'

def is_salon_owner(user, salon_id):
    return user.is_salon_owner and Salon.objects.filter(id=salon_id, owner=user).exists()

def is_assigned_barber(user, salon_id):
    return user.is_barber and SalonAssignment.objects.filter(
        barber=user, salon_id=salon_id, is_active=True
    ).exists()

def assign_salon_permission(user, salon, permission_type):
    SalonPermission.objects.get_or_create(
        salon=salon,
        user=user,
        permission_type=permission_type
    )

def remove_salon_permission(user, salon, permission_type):
    SalonPermission.objects.filter(
        salon=salon,
        user=user,
        permission_type=permission_type
    ).delete()

def assign_owner_permissions(user, salon):
    permission_types = [
        'can_manage', 'can_read', 'can_manage_finance',
        'can_manage_inventory', 'can_manage_shave', 'can_manage_hairstyle', 'can_manage_barbers'
    ]
    for permission_type in permission_types:
        assign_salon_permission(user, salon, permission_type)

def assign_barber_permissions(user, salon, permissions):
    for permission in permissions:
        assign_salon_permission(user, salon, permission)
