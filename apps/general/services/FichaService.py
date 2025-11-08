from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.FichaRepository import FichaRepository


class FichaService(BaseService):
    def __init__(self):
        self.repository = FichaRepository()
