# apps/security/services/role_service.py
from core.base.services.implements.baseService.BaseService import BaseService
from apps.security.repositories.RoleRepository import RoleRepository


class RoleService(BaseService):
    def get_filtered_roles(self, active=None, search=None):
        return self.repository.get_filtered_roles(active, search)
    def __init__(self):
        self.repository = RoleRepository()
    
    def set_active_role_and_users(self, role_id, active):
        """
        Delegar activación/desactivación al repository.
        """
        return self.repository.set_active_role_and_users(role_id, active)

    def list_roles(self):
        """
        Delegar listado al repository.
        """
        return self.repository.list_roles()

    def roles_with_user_count(self):
        """
        Delegar conteo al repository.
        """
        return self.repository.roles_with_user_count()
    