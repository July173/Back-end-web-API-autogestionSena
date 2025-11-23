from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.base.view.implements.BaseViewset import BaseViewSet
from apps.assign.services.RequestAsignationService import RequestAsignationService
from apps.assign.entity.serializers.form.RequestAsignationSerializer import RequestAsignationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.assign.entity.serializers.form.FormRequestSerializer import FormRequestSerializer
from apps.assign.entity.serializers.form.CombinedFormRequestSerializer import CombinedFormRequestSerializer

class RequestAsignationViewset(BaseViewSet):
    service_class = RequestAsignationService
    serializer_class = RequestAsignationSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer(self, *args, **kwargs):
        # Usa FormRequestSerializer solo en acciones específicas
        if hasattr(self, 'action') and self.action in [
            'list_form_requests', 'form_request_detail', 'reject_form_request', 'get_pdf_url'
        ]:
            return FormRequestSerializer(*args, **kwargs)
        return self.serializer_class(*args, **kwargs)
    
    
    #--- List -------
    @swagger_auto_schema(
        operation_description="Obtiene una lista de todas las solicitudes de asignación.",
        tags=["RequestAsignation"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    #--- Create -------
    @swagger_auto_schema(
        operation_description="Crea una nueva solicitud de asignación.",
        tags=["RequestAsignation"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    #--- Retrieve -------
    @swagger_auto_schema(
        operation_description="Obtiene la información de una solicitud específica.",
        tags=["RequestAsignation"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    #--- Update -------
    @swagger_auto_schema(
        operation_description="Actualiza la información completa de una solicitud.",
        tags=["RequestAsignation"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    #--- Partial Update -------
    @swagger_auto_schema(
        operation_description="Actualiza solo algunos campos de una solicitud.",
        tags=["RequestAsignation"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    #--- Destroy -------
    @swagger_auto_schema(
        operation_description="Elimina físicamente una solicitud de la base de datos.",
        tags=["RequestAsignation"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    #--- Soft Destroy -------
    @swagger_auto_schema(
        method='delete',
        operation_description="Realiza un borrado lógico (soft delete) de la solicitud especificada.",
        tags=["RequestAsignation"],
        responses={
            204: openapi.Response("Eliminado lógicamente correctamente."),
            404: openapi.Response("No encontrado.")
        }
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_destroy(self, request, pk=None):
        deleted = self.service_class().soft_delete(pk)
        if deleted:
            return Response(
                {"detail": "Eliminado lógicamente correctamente."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"detail": "No encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
   
    #--- Create Form Request -------
    @swagger_auto_schema(
        operation_description="Crear una nueva solicitud de formulario (sin PDF) — paquete completo (empresa, jefe, talentoHumano, solicitud)",
        tags=["FormRequest"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'empresa': openapi.Schema(type=openapi.TYPE_OBJECT),
                'jefe': openapi.Schema(type=openapi.TYPE_OBJECT),
                'talentoHumano': openapi.Schema(type=openapi.TYPE_OBJECT),
                'solicitud': openapi.Schema(type=openapi.TYPE_OBJECT),
            },
            example={
                "empresa": {"id": None, "nombre": "Nueva empresa SAS", "nit": "123456789", "direccion": "Calle 10", "correo": "empresa@example.com", "telefono": "12345"},
                "jefe": {"id": None, "nombre": "Juan Perez", "correo": "juan@empresa.com", "telefono": "1111"},
                "talentoHumano": {"id": None, "nombre": "Ana Rojas", "correo": "ana@empresa.com", "telefono": "2222"},
                "solicitud": {"apprentice": 1, "ficha": 1, "descripcion": "Necesitamos un aprendizaje", "fecha_inicio_contrato": "2025-11-23", "fecha_fin_contrato": "2026-05-23", "sede": 1, "modality_productive_stage": 1}
            }
        ),
        responses={
            201: openapi.Response("Solicitud creada exitosamente"),
            400: openapi.Response("Error: {'success': False, 'error_type': 'not_found', 'message': 'Entidad no encontrada', 'data': None}")
        }
    )
    @action(detail=False, methods=['post'], url_path='form-request')
    def create_form_request(self, request):
        # Nuevo flujo: aceptar el paquete completo (empresa, jefe, talentoHumano, solicitud)
        serializer = CombinedFormRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Error en los datos de entrada (paquete combinado)',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        result = self.service_class().create_complete_request_package(serializer.validated_data)
        if result['success']:
            request_id = result['data']['request_asignation']['id'] if result['data'] and 'request_asignation' in result['data'] else None
            return Response({
                "message": "Solicitud creada exitosamente",
                "id": request_id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    #--- List Form Requests -------
    @swagger_auto_schema(
        operation_description="Obtener lista de todas las solicitudes de formulario",
        tags=["FormRequest"],   
        responses={
            200: openapi.Response(description="Lista obtenida exitosamente"),
            500: openapi.Response("Error: {'success': False, 'error_type': 'list_form_requests', 'message': 'Error al obtener las solicitudes', 'data': None}")
        }
    )
    @action(detail=False, methods=['get'], url_path='form-request-list')
    def list_form_requests(self, request):
        result = self.service_class().list_form_requests()
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #--- Get PDF URL -------
    @swagger_auto_schema(
        operation_description="Obtiene la URL del PDF de la solicitud.",
        tags=["FormRequest PDF"],
        responses={
            200: openapi.Response("URL del PDF obtenida correctamente."),
            404: openapi.Response("Error: {'success': False, 'error_type': 'not_found', 'message': 'Solicitud no encontrada', 'data': None}")
        }
    )
    @action(detail=True, methods=['get'], url_path='form-request-pdf-url')
    def get_pdf_url(self, request, pk=None):
        result = self.service_class().get_pdf_url(pk)
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
    #--- Reject Form Request -------
    @swagger_auto_schema(
        method='patch',
        operation_description="Rechaza una solicitud de formulario, cambiando el estado y guardando el mensaje de rechazo.",
        tags=["FormRequest"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["rejectionMessage"],
            properties={
                "rejectionMessage": openapi.Schema(type=openapi.TYPE_STRING, description="Motivo del rechazo")
            }
        ),
        responses={
            200: openapi.Response("Solicitud rechazada correctamente."),
            404: openapi.Response("Error: {'success': False, 'error_type': 'not_found', 'message': 'Solicitud no encontrada', 'data': None}")
        }
    )
    @action(detail=True, methods=['patch'], url_path='form-request-reject')
    def reject_form_request(self, request, pk=None):
        rejection_message = request.data.get('rejectionMessage')
        if not rejection_message:
            return Response({
                'success': False,
                'message': 'Debes proporcionar el motivo del rechazo.'
            }, status=status.HTTP_400_BAD_REQUEST)
        result = self.service_class().reject_request(pk, rejection_message)
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
    
    
    #--- Aprendiz Dashboard -------
    @swagger_auto_schema(
        operation_description="Obtiene información del dashboard del aprendiz autenticado (solicitud activa, instructor asignado, estado).",
        tags=["RequestAsignation"],
        manual_parameters=[
            openapi.Parameter(
                'aprendiz_id',
                openapi.IN_QUERY,
                description="ID del aprendiz",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response("Información del dashboard del aprendiz"),
            404: openapi.Response("Aprendiz no encontrado")
        }
    )
    @action(detail=False, methods=['get'], url_path='aprendiz-dashboard')
    def aprendiz_dashboard(self, request):
        aprendiz_id = request.query_params.get('aprendiz_id')
        if not aprendiz_id:
            return Response({
                'success': False,
                'message': 'Se requiere el ID del aprendiz'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = self.service_class().get_aprendiz_dashboard(aprendiz_id)
        if result.get('success', True):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
    
    
    #--- Filter Form Requests -------
    @swagger_auto_schema(
        operation_description="Filtra solicitudes de formulario por búsqueda, estado o programa",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar por nombre o número de documento", type=openapi.TYPE_STRING),
            openapi.Parameter('request_state', openapi.IN_QUERY, description="Filtrar por estado de solicitud", type=openapi.TYPE_STRING),
            openapi.Parameter('program_id', openapi.IN_QUERY, description="Filtrar por ID de programa", type=openapi.TYPE_INTEGER),
            openapi.Parameter('modality_id', openapi.IN_QUERY, description="Filtrar por modalidad de etapa práctica (ID)", type=openapi.TYPE_INTEGER),
        ],
        tags=["FormRequest"],
    )
    @action(detail=False, methods=['get'], url_path='form-request-filtered')
    def filter_form_requests(self, request):
        search = request.query_params.get('search')
        request_state = request.query_params.get('request_state')
        program_id = request.query_params.get('program_id')
        modality_id = request.query_params.get('modality_id')

        result = self.service_class().filter_form_requests(search, request_state, program_id, modality_id)
        return Response(result, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)


    #--- Form Request Detail -------
    @swagger_auto_schema(
        operation_description="Obtiene la información detallada de una solicitud de formulario por su ID.",
        tags=["FormRequest"],
        responses={
            200: openapi.Response("Solicitud encontrada con todos los datos detallados."),
            404: openapi.Response("Error: {'success': False, 'error_type': 'not_found', 'message': 'Solicitud no encontrada', 'data': None}")
        }
    )
    @action(detail=True, methods=['get'], url_path='form-request-detail')
    def form_request_detail(self, request, pk=None):
        result = self.service_class().get_form_request_by_id(pk)
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)