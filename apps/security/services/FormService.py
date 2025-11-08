from core.base.services.implements.baseService.BaseService import BaseService
from apps.security.repositories.FormRepository import FormRepository


class FormService(BaseService):
    def __init__(self):
        self.repository = FormRepository()
