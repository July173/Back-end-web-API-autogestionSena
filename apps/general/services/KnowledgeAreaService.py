from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.KnowledgeAreaRepository import KnowledgeAreaRepository


class KnowledgeAreaService(BaseService):
    def __init__(self):
        self.repository = KnowledgeAreaRepository()
