from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.LegalDocumentRepository import LegalDocumentRepository
from apps.general.entity.models.LegalDocument import LegalDocument


class LegalDocumentService(BaseService):
    def __init__(self):
        self.repository = LegalDocumentRepository()

    def get_filtered_legal_documents(self, active=None, search=None):
        queryset = LegalDocument.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

    def update(self, id, data):
        from django.utils import timezone
        data['last_update'] = timezone.now().date()
        return super().update(id, data)
