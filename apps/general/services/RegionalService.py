from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.RegionalRepository import RegionalRepository
from apps.general.entity.models import Regional


class RegionalService(BaseService):
    def __init__(self):
        self.repository = RegionalRepository()
    
    def get_regional_with_centers_by_id(self, pk):
        """Obtiene una regional por ID con sus centros anidados"""
        try:
            return Regional.objects.prefetch_related('centers').get(pk=pk)
        except Regional.DoesNotExist:
            return None
    
    def get_all_regionals_with_centers(self):
        """Obtiene todas las regionales con sus centros anidados"""
        return Regional.objects.prefetch_related('centers').all()
