from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.SupportContactRepository import SupportContactRepository

class SupportContactService(BaseService):
    def __init__(self):
        self.repository = SupportContactRepository()
