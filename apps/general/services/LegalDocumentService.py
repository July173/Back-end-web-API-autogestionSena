from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.LegalDocumentRepository import LegalDocumentRepository

class LegalDocumentService(BaseService):
    def __init__(self):
        self.repository = LegalDocumentRepository()

    def update(self, id, data):
        from django.utils import timezone
        data['last_update'] = timezone.now().date()
        return super().update(id, data)
