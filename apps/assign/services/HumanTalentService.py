from core.base.services.implements.baseService.BaseService import BaseService
from apps.assign.repositories.HumanTalentRepository import HumanTalentRepository


class HumanTalentService(BaseService):
    def __init__(self):
        self.repository = HumanTalentRepository()
