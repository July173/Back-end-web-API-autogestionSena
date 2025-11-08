from core.base.repositories.implements.baseRepository.BaseRepository import BaseRepository
from apps.assign.entity.models import RequestAsignation
from apps.assign.entity.enums.request_state_enum import RequestState
from django.db.models import Q
from apps.general.entity.models import PersonSede
from apps.general.entity.models import Apprentice, Sede
from apps.assign.entity.models import Enterprise, Boss, HumanTalent, ModalityProductiveStage, RequestAsignation
from django.db import transaction
from apps.general.entity.models import Ficha
import logging

logger = logging.getLogger(__name__)


class RequestAsignationRepository(BaseRepository):

    def __init__(self):
        super().__init__(RequestAsignation)

    def filter_form_requests(self, search=None, request_state=None, program_id=None):
        queryset = RequestAsignation.objects.select_related(
            'aprendiz__person',
            'aprendiz__ficha__program',
            'enterprise',
            'modality_productive_stage'
        ).all()

        #  Filtro por texto (nombre o número de documento)
        if search:
            queryset = queryset.filter(
                Q(aprendiz__person__first_name__icontains=search) |
                Q(aprendiz__person__first_last_name__icontains=search) |
                Q(aprendiz__person__second_last_name__icontains=search) |
                Q(aprendiz__person__number_identification__icontains=search)
            )

        #  Filtro por estado
        if request_state:
            queryset = queryset.filter(request_state=request_state)

        #  Filtro por programa
        if program_id:
            queryset = queryset.filter(aprendiz__ficha__program_id=program_id)

        return queryset

    
    def get_form_request_by_id(self, request_id):
        """
        Obtener una solicitud de formulario por su ID con todas sus relaciones.
        """
        try:
            request_asignation = RequestAsignation.objects.select_related(
                'aprendiz__person',
                'aprendiz__ficha',
                'enterprise',
                'enterprise__boss',
                'enterprise__human_talent',
                'modality_productive_stage'
            ).get(pk=request_id)
            if hasattr(request_asignation.enterprise, 'boss') and hasattr(request_asignation.enterprise, 'human_talent'):
                modality = request_asignation.modality_productive_stage
                regional = getattr(modality, 'regional', None)
                center = getattr(modality, 'center', None)
                sede = getattr(modality, 'sede', None)
                return (
                    request_asignation.aprendiz.person,
                    request_asignation.aprendiz,
                    request_asignation.enterprise,
                    request_asignation.enterprise.boss,
                    request_asignation.enterprise.human_talent,
                    modality,
                    request_asignation,
                    regional,
                    center,
                    sede
                )
            else:
                return None
        except RequestAsignation.DoesNotExist:
            return None


    def create_all_dates_form_request(self, data):
        """
        Crea las entidades relacionadas con la solicitud de formulario en una sola transacción.
        Vincula el aprendiz existente y actualiza su ficha.
        """
        
        with transaction.atomic():
            logger.info(f"Iniciando creación de solicitud para {data.get('person_first_name')} {data.get('person_first_last_name')} {data.get('person_second_last_name', '')}")
            
            # OBTENER ENTIDADES DE REFERENCIA (solo comunicación BD)
            sede = Sede.objects.get(pk=data['sede'])
            modality = ModalityProductiveStage.objects.get(pk=data['modality_productive_stage'])
            
            # Buscar aprendiz existente
            aprendiz = Apprentice.objects.get(pk=data['aprendiz_id'])
            
            # Buscar ficha y vincularla al aprendiz
            ficha = Ficha.objects.get(pk=data['ficha_id'])
            aprendiz.ficha = ficha
            aprendiz.save()
            
            # CREACIÓN DE ENTIDADES (solo operaciones BD)
            
            # 3. Crear Enterprise
            enterprise_data = {
                'name_enterprise': data['enterprise_name'],
                'nit_enterprise': data['enterprise_nit'],
                'locate': data['enterprise_location'],
                'email_enterprise': data['enterprise_email'],
            }
            enterprise = Enterprise.objects.create(**enterprise_data)
            logger.info(f"Empresa creada con ID: {enterprise.id}")
            
            # 4. Crear Boss
            boss_data = {
                'enterprise': enterprise,
                'name_boss': data['boss_name'],
                'phone_number': data['boss_phone'],
                'email_boss': data['boss_email'],
                'position': data['boss_position'],
            }
            boss = Boss.objects.create(**boss_data)
            logger.info(f"Jefe creado con ID: {boss.id}")
            
            # 5. Crear HumanTalent
            human_talent_data = {
                'enterprise': enterprise,
                'name': data['human_talent_name'],
                'email': data['human_talent_email'],
                'phone_number': data['human_talent_phone'],
            }
            human_talent = HumanTalent.objects.create(**human_talent_data)
            logger.info(f"Talento humano creado con ID: {human_talent.id}")
            
            # 6. Crear RequestAsignation con PDF
            request_asignation_data = {
                'aprendiz': aprendiz,
                'enterprise': enterprise,
                'modality_productive_stage': modality,
                'request_date': data['fecha_inicio_contrato'],  # Usar fecha de inicio como fecha de solicitud
                'date_start_production_stage': data['fecha_inicio_contrato'],
                'date_end_production_stage': data['fecha_fin_contrato'],
                'pdf_request': data.get('pdf_request'),  # El archivo PDF
                 'request_state': RequestState.SIN_ASIGNAR,  # Estado inicial correcto del enum
            }
            request_asignation = RequestAsignation.objects.create(**request_asignation_data)
            logger.info(f"RequestAsignation creado con ID: {request_asignation.id}, PDF: {request_asignation.pdf_request}")
            
            logger.info("Solicitud de formulario creada exitosamente")
            
            # Retornar instancias directamente (incluyendo request_asignation)
            return aprendiz, ficha, enterprise, boss, human_talent, sede, modality, request_asignation


    def get_all_form_requests(self):
        """
        Obtener todas las solicitudes de formulario con sus relaciones.
        Usa RequestAsignation como tabla principal que conecta todo.
        """
        logger.info("Obteniendo todas las solicitudes de formulario")
        
        # Obtener todas las RequestAsignation con sus relaciones optimizadas
        request_asignations = RequestAsignation.objects.select_related(
            'aprendiz__person',           # Person a través de Aprendiz
            'aprendiz__ficha',            # Ficha del aprendiz
            'enterprise',                 # Enterprise
            'enterprise__boss',           # Boss (OneToOne)
            'enterprise__human_talent',   # HumanTalent (OneToOne)
            'modality_productive_stage'   # ModalityProductiveStage
        ).all()
        
        # Lista para almacenar las solicitudes encontradas
        form_requests = []
        
        for request_asignation in request_asignations:
            # Verificar que tenga boss y human talent
            if hasattr(request_asignation.enterprise, 'boss') and hasattr(request_asignation.enterprise, 'human_talent'):
                modality = request_asignation.modality_productive_stage
                regional = getattr(modality, 'regional', None)
                center = getattr(modality, 'center', None)
                sede = getattr(modality, 'sede', None)
                # Crear tupla con las entidades relacionadas
                # Obtener la sede a través de PersonSede
                person = request_asignation.aprendiz.person
                person_sede = PersonSede.objects.filter(PersonId=person).first()
                sede = person_sede.SedeId if person_sede and person_sede.SedeId else None
                form_request = (
                    person,
                    request_asignation.aprendiz,
                    request_asignation.enterprise,
                    request_asignation.enterprise.boss,
                    request_asignation.enterprise.human_talent,
                    sede,
                    modality,
                    request_asignation
                )
                form_requests.append(form_request)

        logger.info(f"Se encontraron {len(form_requests)} solicitudes")
        return form_requests
    

    

