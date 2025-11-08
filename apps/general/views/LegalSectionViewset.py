from rest_framework import status
from core.base.view.implements.BaseViewset import BaseViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.general.entity.models.LegalSection import LegalSection
from apps.general.entity.serializers.LegalSectionSerializer import LegalSectionSerializer
from apps.general.services.LegalSectionService import LegalSectionService
from rest_framework.decorators import action



class LegalSectionViewset(BaseViewSet):
    service_class = LegalSectionService
    serializer_class = LegalSectionSerializer

    @swagger_auto_schema(
        operation_description="Obtiene una lista de todas las secciones legales registradas.",
        tags=["LegalSection"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Crea una nueva sección legal.",
        tags=["LegalSection"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Obtiene la información de una sección legal específica.",
        tags=["LegalSection"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Actualiza la información completa de una sección legal.",
        tags=["LegalSection"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Actualiza solo algunos campos de una sección legal.",
        tags=["LegalSection"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Elimina físicamente una sección legal de la base de datos.",
        tags=["LegalSection"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Realiza un borrado lógico de la sección legal especificada.",
        tags=["LegalSection"]
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_destroy(self, request, pk=None):
        """
        Realiza un borrado lógico de la sección legal especificada.
        """
        return super().soft_destroy(request, pk)
