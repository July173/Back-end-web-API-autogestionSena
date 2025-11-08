from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.SupportScheduleRepository import SupportScheduleRepository

class SupportScheduleService(BaseService):
    """
    Servicio para operaciones de negocio sobre SupportSchedule.
    """
    def __init__(self):
        self.repository = SupportScheduleRepository()
