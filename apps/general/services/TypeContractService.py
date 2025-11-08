from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.TypeContractRepository import TypeContractRepository

class TypeContractService(BaseService):
    def __init__(self):
        super().__init__(TypeContractRepository())
