from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.FichaRepository import FichaRepository
from apps.general.entity.models import Ficha



class FichaService(BaseService):
    def get_filtered_fichas(self, active=None, search=None):
        queryset = Ficha.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(file_number__icontains=search)
        return queryset
    def __init__(self):
        self.repository = FichaRepository()
