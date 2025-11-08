from core.base.services.implements.baseService.BaseService import BaseService
from apps.security.repositories.DocumentTypeRepository import DocumentTypeRepository

class DocumentTypeService(BaseService):
    def __init__(self):
        super().__init__(DocumentTypeRepository())
