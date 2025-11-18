from core.base.services.implements.baseService.BaseService import BaseService
from apps.security.repositories.ModuleRepository import ModuleRepository


class ModuleService(BaseService):
    def create_module(self, validated_data):
        from apps.security.entity.models import Module
        name = validated_data.get('name', '').strip()
        if not name:
            return None, "El nombre es requerido."
        exists = Module.objects.filter(name__iexact=name, delete_at__isnull=True).exists()
        if exists:
            return None, "Ya existe un módulo con ese nombre."
        serializer = self.repository.get_serializer()(data=validated_data)
        if serializer.is_valid():
            instance = serializer.save()
            return instance, None
        return None, serializer.errors

    def get_filtered_modules(self, active=None, search=None):
        return self.repository.get_filtered_modules(active, search)

    def __init__(self):
        super().__init__(ModuleRepository())
