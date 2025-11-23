from core.base.services.implements.baseService.BaseService import BaseService
from apps.assign.repositories.RequestAsignationRepository import RequestAsignationRepository
from django.db import transaction
import logging
from apps.general.entity.models import Apprentice, Ficha, Sede
from apps.assign.entity.models import ModalityProductiveStage
from apps.assign.entity.enums.request_state_enum import RequestState
from apps.assign.entity.models import RequestAsignation
from apps.security.emails.SolicitudRechazada import send_rejection_email
from apps.security.entity.models import User
from apps.assign.entity.models import RequestAsignation
from apps.general.entity.models import PersonSede
from dateutil.relativedelta import relativedelta
from apps.assign.entity.models import AsignationInstructor

logger = logging.getLogger(__name__)


class RequestAsignationService(BaseService):
    def __init__(self):
        self.repository = RequestAsignationRepository()

    def error_response(self, message, error_type="error"):
        return {"success": False, "error_type": error_type, "message": str(message), "data": None}

    def get_pdf_url(self, request_id):
        try:
            solicitud = RequestAsignation.objects.get(pk=request_id)
            if solicitud.pdf_request:
                return {
                    'success': True,
                    'pdf_url': solicitud.pdf_request.url
                }
            else:
                return self.error_response('La solicitud no tiene PDF adjunto.', "no_pdf")
        except RequestAsignation.DoesNotExist:
            return self.error_response('Solicitud no encontrada.', "not_found")
        except Exception as e:
            return self.error_response(f"Error al obtener PDF: {e}", "get_pdf_url")

    def reject_request(self, request_id, rejection_message):
        try:
            request = RequestAsignation.objects.get(pk=request_id)
            request.request_state = RequestState.RECHAZADO
            request.rejectionMessage = rejection_message
            request.save()
            apprentice = request.apprentice
            person = apprentice.person
            nombre_aprendiz = f"{person.first_name} {person.first_last_name}"
            user = User.objects.filter(person=person).first()
            email = user.email if user else None
            if email:
                send_rejection_email(email, nombre_aprendiz, rejection_message)
            return {
                'success': True,
                'message': 'Solicitud rechazada correctamente',
                'data': {
                    'id': request.id,
                    'request_state': request.request_state,
                    'rejectionMessage': request.rejectionMessage
                }
            }
        except RequestAsignation.DoesNotExist:
            return self.error_response('Solicitud no encontrada', "not_found")
        except Exception as e:
            return self.error_response(f"Error al rechazar solicitud: {e}", "reject_request")

    def get_form_request_by_id(self, request_id):
        try:
            result = self.repository.get_form_request_by_id(request_id)
            if not result:
                return self.error_response('Solicitud no encontrada', "not_found")
            person, aprendiz, enterprise, boss, human_talent, modality, request_asignation, regional, center, sede = result
            request_item = {
                'aprendiz_id': aprendiz.id,
                'ficha_id': aprendiz.ficha_id if aprendiz.ficha else None,
                'fecha_inicio_contrato': request_asignation.date_start_production_stage,
                'fecha_fin_contrato': getattr(request_asignation, 'date_end_production_stage', None),
                'enterprise_name': enterprise.name_enterprise,
                'enterprise_nit': enterprise.nit_enterprise,
                'enterprise_location': enterprise.locate,
                'enterprise_email': enterprise.email_enterprise,
                'boss_name': boss.name_boss,
                'boss_phone': boss.phone_number,
                'boss_email': boss.email_boss,
                'boss_position': boss.position,
                'human_talent_name': human_talent.name,
                'human_talent_email': human_talent.email,
                'human_talent_phone': human_talent.phone_number,
                'regional': regional.id if regional else None,
                'center': center.id if center else None,
                'sede': sede.id if sede else None,
                'modality_productive_stage': modality.id,
                'request_state': request_asignation.request_state
            }
            person, aprendiz, enterprise, boss, human_talent, modality, request_asignation, regional, center, sede = result
            # Obtener correo del aprendiz desde User
            user = User.objects.filter(person=person).first()
            correo_aprendiz = user.email if user else None
            # Obtener sede, centro y regional desde PersonSede
            personsede = PersonSede.objects.filter(person=person).first()
            sede_obj = personsede.sede if personsede else sede
            center_obj = sede_obj.center if sede_obj and hasattr(sede_obj, 'center') else center
            regional_obj = center_obj.regional if center_obj and hasattr(center_obj, 'regional') else regional
            # Datos de talento humano
            talento_humano = {
                'nombre': getattr(human_talent, 'name', None),
                'correo': getattr(human_talent, 'email', None),
                'telefono': getattr(human_talent, 'phone_number', None)
            } if human_talent else None
            # Obtener número de ficha y nombre del programa
            ficha = aprendiz.ficha if hasattr(aprendiz, 'ficha') and aprendiz.ficha else None
            numero_ficha = ficha.file_number if ficha and hasattr(ficha, 'file_number') else None
            programa = ficha.program if ficha and hasattr(ficha, 'program') else None
            nombre_programa = programa.name if programa and hasattr(programa, 'name') else None
            request_item = {
                'aprendiz_id': aprendiz.id,
                'nombre_aprendiz': f"{getattr(person, 'first_name', '')} {getattr(person, 'first_last_name', '')} {getattr(person, 'second_last_name', '')}",
                'tipo_identificacion': getattr(person, 'type_identification_id', None),
                'numero_identificacion': getattr(person, 'number_identification', None),
                'telefono_aprendiz': getattr(person, 'phone_number', None),
                'correo_aprendiz': correo_aprendiz,
                'ficha_id': ficha.id if ficha else None,
                'numero_ficha': numero_ficha,
                'programa': nombre_programa,
                'empresa_nombre': enterprise.name_enterprise,
                'empresa_nit': enterprise.nit_enterprise,
                'empresa_ubicacion': enterprise.locate,
                'empresa_correo': enterprise.email_enterprise,
                'jefe_nombre': boss.name_boss,
                'jefe_telefono': boss.phone_number,
                'jefe_correo': boss.email_boss,
                'jefe_cargo': boss.position,
                'regional': regional_obj.name if regional_obj else None,
                'center': center_obj.name if center_obj else None,
                'sede': sede_obj.name if sede_obj else None,
                'fecha_solicitud': request_asignation.request_date,
                'fecha_inicio_etapa_practica': request_asignation.date_start_production_stage,
                'fecha_fin_etapa_practica': getattr(request_asignation, 'date_end_production_stage', None),
                'modality_productive_stage': modality.name_modality if hasattr(modality, 'name_modality') else None,
                'request_state': request_asignation.request_state,
                'pdf_url': request_asignation.pdf_request.url if request_asignation.pdf_request else None,
                'talento_humano': talento_humano
            }
            return {
                'success': True,
                'message': 'Solicitud encontrada',
                'data': request_item
            }
        except RequestAsignation.DoesNotExist:
            return self.error_response('Solicitud no encontrada', "not_found")
        except Exception as e:
            return self.error_response(f"Error al obtener la solicitud: {e}", "get_form_request_by_id")

    def create_form_request(self, validated_data):
        try:
            logger.info(f"Iniciando creación de solicitud para aprendiz ID: {validated_data.get('apprentice')}")
            apprentice = Apprentice.objects.get(pk=validated_data['apprentice'])
            ficha = Ficha.objects.get(pk=validated_data['ficha'])
            last_request = RequestAsignation.objects.filter(apprentice=apprentice).order_by('-id').first()
            if last_request and last_request.request_state != RequestState.RECHAZADO:
                return self.error_response("Solo puedes volver a enviar el formulario si tu última solicitud fue rechazada.", "invalid_state")
            sede = Sede.objects.get(pk=validated_data['sede'])
            ModalityProductiveStage.objects.get(pk=validated_data['modality_productive_stage'])
            fecha_inicio = validated_data.get('fecha_inicio_contrato')
            fecha_fin = validated_data.get('fecha_fin_contrato')
            if fecha_inicio and fecha_fin:
                diferencia = relativedelta(fecha_fin, fecha_inicio)
                meses = diferencia.years * 12 + diferencia.months
                if meses < 6 or (meses == 6 and diferencia.days < 0):
                    return self.error_response("La diferencia entre la fecha de inicio y fin de contrato debe ser de al menos 6 meses.", "invalid_dates")
            logger.info("Validaciones completadas exitosamente")
            with transaction.atomic():
                apprentice_obj, ficha_obj, enterprise, boss, human_talent, sede, modality, request_asignation = self.repository.create_all_dates_form_request(validated_data)
                person = apprentice_obj.person
                PersonSede.objects.update_or_create(
                    person=person,
                    defaults={"sede": sede}
                )
                response = {
                    'success': True,
                    'message': 'Solicitud creada exitosamente',
                    'data': {
                        'aprendiz': {
                            'id': apprentice_obj.id,
                            'ficha_id': ficha_obj.id,
                            'active': apprentice_obj.active
                        },
                        'enterprise': {
                            'id': enterprise.id,
                            'name': enterprise.name_enterprise,
                            'nit': enterprise.nit_enterprise,
                            'location': enterprise.locate,
                            'email': enterprise.email_enterprise
                        },
                        'boss': {
                            'id': boss.id,
                            'name': boss.name_boss,
                            'phone': boss.phone_number,
                            'email': boss.email_boss,
                            'position': boss.position
                        },
                        'human_talent': {
                            'id': human_talent.id,
                            'name': human_talent.name,
                            'email': human_talent.email,
                            'phone': human_talent.phone_number
                        },
                        'references': {
                            'sede': {'id': sede.id, 'name': sede.name},
                            'modality': {'id': modality.id, 'name': modality.name_modality}
                        },
                        'request_asignation': {
                            'id': request_asignation.id,
                            'request_date': request_asignation.request_date,
                            'date_start_production_stage': request_asignation.date_start_production_stage,
                            'date_end_production_stage': getattr(request_asignation, 'date_end_production_stage', None),
                            'request_state': request_asignation.request_state
                        }
                    }
                }
                logger.info("Solicitud creada exitosamente")
                return response
        except (Apprentice.DoesNotExist, Ficha.DoesNotExist) as e:
            return self.error_response(f"Entidad no encontrada: {str(e)}", "not_found")
        except (Sede.DoesNotExist, ModalityProductiveStage.DoesNotExist) as e:
            return self.error_response(f"Entidad de referencia no encontrada: {str(e)}", "not_found")
        except Exception as e:
            return self.error_response(f"Error al crear solicitud: {e}", "create_form_request")

    def list_form_requests(self):
        """
        Listar solicitudes mostrando solo Nombre, Tipo de identificación, Número y Fecha Solicitud.
        """
        try:
            logger.info("Obteniendo lista de solicitudes (solo datos personales básicos)")
            form_requests = self.repository.get_all_form_requests()
            requests_data = []
            for person, aprendiz, enterprise, boss, human_talent, sede, modality, request_asignation in form_requests:
                request_item = {
                    'id': request_asignation.id,  # id de la solicitud
                    'aprendiz_id': aprendiz.id,   # id del aprendiz
                    'nombre': f"{getattr(person, 'first_name', '')} {getattr(person, 'first_last_name', '')} {getattr(person, 'second_last_name', '')}",
                    'tipo_identificacion': getattr(person, 'type_identification_id', None),
                    'numero_identificacion': getattr(person, 'number_identification', None),
                    'fecha_solicitud': request_asignation.request_date,
                    'request_state': request_asignation.request_state,
                    'nombre_modalidad': getattr(modality, 'name_modality', None) if modality else None
                }
                requests_data.append(request_item)
            logger.info(f"Se encontraron {len(requests_data)} solicitudes")
            return {
                'success': True,
                'message': f'Se encontraron {len(requests_data)} solicitudes',
                'count': len(requests_data),
                'data': requests_data
            }
        except Exception as e:
            logger.error(f"Error al listar solicitudes: {str(e)}")
            return self.error_response(f"Error al obtener las solicitudes: {str(e)}", "list_form_requests")

    def get_aprendiz_dashboard(self, aprendiz_id):
        """
        Obtiene la información del dashboard del aprendiz:
        - Estado de la solicitud activa
        - Instructor asignado (si existe)
        - Detalles de la solicitud
        """
        try:
            
            
            aprendiz = Apprentice.objects.select_related('person', 'ficha').get(pk=aprendiz_id)
            
            # Buscar la solicitud más reciente del aprendiz
            latest_request = RequestAsignation.objects.filter(
                aprendiz=aprendiz
            ).select_related(
                'enterprise',
                'enterprise__boss',
                'modality_productive_stage'
            ).order_by('-request_date').first()
            
            result = {
                'has_request': latest_request is not None,
                'request': None,
                'instructor': None,
                'request_state': None
            }
            
            if latest_request:
                # Obtener el nombre del boss si existe
                boss_name = None
                if hasattr(latest_request.enterprise, 'boss') and latest_request.enterprise.boss:
                    boss_name = latest_request.enterprise.boss.name_boss
                
                # Información de la solicitud
                result['request'] = {
                    'id': latest_request.id,
                    'enterprise_name': latest_request.enterprise.name_enterprise if latest_request.enterprise else None,
                    'boss_name': boss_name,
                    'modality': latest_request.modality_productive_stage.name_modality if latest_request.modality_productive_stage else None,
                    'start_date': str(latest_request.date_start_production_stage),
                    'end_date': str(latest_request.date_end_production_stage),
                    'request_date': str(latest_request.request_date),
                    'request_state': latest_request.request_state,
                    'pdf_url': latest_request.pdf_request.url if latest_request.pdf_request else None,
                }
                result['request_state'] = latest_request.request_state
                
                # Buscar si tiene instructor asignado
                asignacion = AsignationInstructor.objects.filter(
                    request_asignation=latest_request
                ).select_related('instructor__person', 'instructor__knowledgeArea').first()
                
                if asignacion:
                    from apps.security.entity.models import User
                    instructor = asignacion.instructor
                    
                    # Obtener el email del usuario relacionado con la persona del instructor
                    email = None
                    try:
                        user = User.objects.filter(person=instructor.person).first()
                        if user:
                            email = user.email
                    except:
                        pass
                    
                    result['instructor'] = {
                        'id': instructor.id,
                        'first_name': instructor.person.first_name,
                        'second_name': instructor.person.second_name,
                        'first_last_name': instructor.person.first_last_name,
                        'second_last_name': instructor.person.second_last_name,
                        'email': email,
                        'phone': instructor.person.phone_number,
                        'knowledge_area': instructor.knowledgeArea.name if instructor.knowledgeArea else None,
                        'assigned_at': str(latest_request.request_date),
                    }
            
            return result
            
        except Apprentice.DoesNotExist:
            return self.error_response('Aprendiz no encontrado', 'not_found')
        except Exception as e:
            logger.error(f"Error al obtener dashboard del aprendiz: {str(e)}")
            return self.error_response(f"Error al obtener información del dashboard: {str(e)}", "dashboard_error")


    def filter_form_requests(self, search=None, request_state=None, program_id=None, modality_id=None):
        try:
            requests = self.repository.filter_form_requests(search, request_state, program_id, modality_id)
            data = []

            for req in requests:
                person = req.apprentice.person
                ficha = req.apprentice.ficha
                programa = ficha.program.name if ficha and hasattr(ficha, 'program') and ficha.program else None
                data.append({
                    "id": req.id,
                    "apprentice_id": req.apprentice.id,
                    "nombre": f"{person.first_name} {person.first_last_name} {person.second_last_name}",
                    "tipo_identificacion": getattr(person, 'type_identification_id', None),
                    "numero_identificacion": str(person.number_identification),
                    "fecha_solicitud": str(req.request_date),
                    "request_state": req.request_state,
                    "programa": programa,
                    "modalidad": getattr(req.modality_productive_stage, 'name_modality', None) if hasattr(req, 'modality_productive_stage') else None,
                    "modalidad_id": req.modality_productive_stage.id if getattr(req, 'modality_productive_stage', None) else None
                })

            return {
                "success": True,
                "count": len(data),
                "data": data
            }

        except Exception as e:
            return self.error_response(f"Error al filtrar solicitudes: {e}", "filter_form_requests")
