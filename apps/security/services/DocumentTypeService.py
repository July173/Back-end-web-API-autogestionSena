from core.base.services.implements.baseService.BaseService import BaseService
from apps.security.repositories.DocumentTypeRepository import DocumentTypeRepository
from apps.security.entity.models.DocumentType import DocumentType


class DocumentTypeService(BaseService):
    def get_filtered_document_types(self, active=None, search=None):
        queryset = DocumentType.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def __init__(self):
        super().__init__(DocumentTypeRepository())
