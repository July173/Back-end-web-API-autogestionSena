from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.TypeOfQueriesRepository import TypeOfQueriesRepository

class TypeOfQueriesService(BaseService):
    """
    Servicio para operaciones de negocio sobre TypeOfQueries.
    """
    def __init__(self):
        self.repository = TypeOfQueriesRepository()
