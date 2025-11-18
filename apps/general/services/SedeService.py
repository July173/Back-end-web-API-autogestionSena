from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.SedeRepository import SedeRepository
from apps.general.entity.models.Sede import Sede


class SedeService(BaseService):
    def __init__(self):
        self.repository = SedeRepository()

    def get_filtered_sedes(self, active=None, search=None):        
        queryset = Sede.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
