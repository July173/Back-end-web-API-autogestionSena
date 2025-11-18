from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.LegalSectionRepository import LegalSectionRepository
from apps.general.entity.models.LegalSection import LegalSection


class LegalSectionService(BaseService):
    def __init__(self):
        super().__init__(LegalSectionRepository())

    def get_filtered_legal_sections(self, active=None, search=None):        
        queryset = LegalSection.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset