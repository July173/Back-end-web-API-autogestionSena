from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.ColorsRepository import ColorsRepository


class ColorsService(BaseService):
    def get_filtered_colors(self, active=None, search=None):
        from apps.general.entity.models.Colors import Colors
        queryset = Colors.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def __init__(self):
        super().__init__(ColorsRepository())
