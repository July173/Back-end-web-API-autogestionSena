from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.CenterRepository import CenterRepository
from apps.general.entity.models import Center

class CenterService(BaseService):
    def __init__(self):
        self.repository = CenterRepository()
    
    def get_center_with_sedes_by_id(self, pk):
            """Delegar la consulta al repository."""
            return self.repository.get_center_with_sedes_by_id(pk)

    def get_all_centers_with_sedes(self):
            """Delegar la consulta al repository."""
            return self.repository.get_all_centers_with_sedes()
