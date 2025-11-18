from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.SupportScheduleRepository import SupportScheduleRepository
from apps.general.entity.models.SupportSchedule import SupportSchedule


class SupportScheduleService(BaseService):
    def __init__(self):
        self.repository = SupportScheduleRepository()

    def get_filtered_support_schedules(self, active=None, search=None):        
        queryset = SupportSchedule.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(day_range__icontains=search)
        return queryset
