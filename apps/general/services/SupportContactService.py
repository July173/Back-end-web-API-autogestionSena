from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.SupportContactRepository import SupportContactRepository
from apps.general.entity.models.SupportContact import SupportContact


class SupportContactService(BaseService):
    def __init__(self):
        self.repository = SupportContactRepository()

    def get_filtered_support_contacts(self, active=None, search=None):        
        queryset = SupportContact.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(type__icontains=search)
        return queryset
