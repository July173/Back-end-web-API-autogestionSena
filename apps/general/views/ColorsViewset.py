from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.base.view.implements.BaseViewset import BaseViewSet
from apps.general.services.ColorsService import ColorsService
from apps.general.entity.serializers.ColorsSerializer import ColorsSerializer

class ColorsViewset(BaseViewSet):
    
    service_class = ColorsService
    serializer_class = ColorsSerializer

    @swagger_auto_schema(
        operation_description="Obtiene una lista de todos los colores registrados.",
        tags=["Colors"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # ----------- CREATE -----------
    @swagger_auto_schema(
        operation_description="Crea un nuevo color.",
        tags=["Colors"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    # ----------- RETRIEVE -----------
    @swagger_auto_schema(
        operation_description="Obtiene la información de un color específico.",
        tags=["Colors"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # ----------- UPDATE -----------
    @swagger_auto_schema(
        operation_description="Actualiza la información completa de un color.",
        tags=["Colors"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    # ----------- PARTIAL UPDATE -----------
    @swagger_auto_schema(
        operation_description="Actualiza solo algunos campos de un color.",
        tags=["Colors"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    # ----------- DELETE -----------
    @swagger_auto_schema(
        operation_description="Elimina físicamente un color de la base de datos.",
        tags=["Colors"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
     # ----------- SOFT DELETE (custom) -----------

    @swagger_auto_schema(
        method='delete',
        operation_description="Realiza un borrado lógico (soft delete) del color especificado.",
        tags=["Colors"],
        responses={
            204: openapi.Response("Eliminado lógicamente correctamente."),
            404: openapi.Response("No encontrado.")
        }
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_destroy(self, request, pk=None):
        """
        Realiza un borrado lógico del color especificado.
        """
        return super().soft_destroy(request, pk)
   