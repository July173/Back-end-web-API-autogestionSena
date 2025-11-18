from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.TypeOfQueriesRepository import TypeOfQueriesRepository
from apps.general.entity.models.TypeOfQueries import TypeOfQueries


class TypeOfQueriesService(BaseService):
    def __init__(self):
        self.repository = TypeOfQueriesRepository()

    def get_filtered_type_of_queries(self, active=None, search=None):        
        queryset = TypeOfQueries.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
