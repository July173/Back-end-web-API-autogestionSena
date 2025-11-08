from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.LegalSectionRepository import LegalSectionRepository

class LegalSectionService(BaseService):
    def __init__(self):
        super().__init__(LegalSectionRepository())