from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.TypeContractRepository import TypeContractRepository
from apps.general.entity.models.TypeContract import TypeContract


class TypeContractService(BaseService):
    def __init__(self):
        super().__init__(TypeContractRepository())

    def get_filtered_type_contracts(self, active=None, search=None):        
        queryset = TypeContract.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
