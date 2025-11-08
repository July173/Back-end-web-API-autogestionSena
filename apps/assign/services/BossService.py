from core.base.services.implements.baseService.BaseService import BaseService
from apps.assign.repositories.BossRepository import BossRepository


class BossService(BaseService):
    def __init__(self):
        self.repository = BossRepository()
