from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.SedeRepository import SedeRepository


class SedeService(BaseService):
    def __init__(self):
        self.repository = SedeRepository()
