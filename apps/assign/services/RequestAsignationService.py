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
from django.utils.dateparse import parse_date
from apps.assign.entity.models import Enterprise, Boss, HumanTalent
from django.core.exceptions import ValidationError
from django.utils import timezone


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
                'boss_name': boss.name_boss if boss else None,
                'boss_phone': boss.phone_number if boss else None,
                'boss_email': boss.email_boss if boss else None,
                'boss_position': boss.position if boss else None,
                'human_talent_name': human_talent.name if human_talent else None,
                'human_talent_email': human_talent.email if human_talent else None,
                'human_talent_phone': human_talent.phone_number if human_talent else None,
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
                    'nombre_modalidad': getattr(modality, 'name_modality', None) if modality else None,
                    'boss': boss.name_boss if boss else None,
                    'human_talent': human_talent.name if human_talent else None
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
            # Boss es una relación 1:N (Boss.enterprise FK) -> usar prefetch_related para traer bosses
            latest_request = RequestAsignation.objects.filter(
                aprendiz=aprendiz
            ).select_related(
                'enterprise',
                'modality_productive_stage'
            ).prefetch_related('enterprise__bosses').order_by('-request_date').first()
            
            result = {
                'has_request': latest_request is not None,
                'request': None,
                'instructor': None,
                'request_state': None
            }
            
            if latest_request:
                # Obtener el nombre del boss si existe
                boss_name = None
                # Obtener primer boss si existe
                if latest_request.enterprise and latest_request.enterprise.bosses.exists():
                    boss_obj = latest_request.enterprise.bosses.first()
                    boss_name = boss_obj.name_boss if boss_obj else None
                
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


    def update_request_state(self, request_id, request_state=None, fecha_inicio=None, fecha_fin=None):
        """
        Update the request_asignation state and optionally the start/end dates.
        Returns a dict with the same structure as other service methods.
        """
        try:
            req = RequestAsignation.objects.get(pk=request_id)

            # Parse date strings if provided
            
            if isinstance(fecha_inicio, str):
                fecha_inicio_parsed = parse_date(fecha_inicio)
            else:
                fecha_inicio_parsed = fecha_inicio

            if isinstance(fecha_fin, str):
                fecha_fin_parsed = parse_date(fecha_fin)
            else:
                fecha_fin_parsed = fecha_fin

            # If both dates provided, validate ordering and minimal 6 months difference
            if fecha_inicio_parsed and fecha_fin_parsed:
                diferencia = relativedelta(fecha_fin_parsed, fecha_inicio_parsed)
                meses = diferencia.years * 12 + diferencia.months
                if meses < 6 or (meses == 6 and diferencia.days < 0):
                    return self.error_response("La diferencia entre la fecha de inicio y fin de contrato debe ser de al menos 6 meses.", "invalid_dates")

            # Apply updates
            updated = False
            if request_state is not None:
                req.request_state = request_state
                updated = True

            if fecha_inicio_parsed is not None:
                req.date_start_production_stage = fecha_inicio_parsed
                updated = True

            if fecha_fin_parsed is not None:
                req.date_end_production_stage = fecha_fin_parsed
                updated = True

            if updated:
                req.save()

            return {
                'success': True,
                'message': 'Solicitud actualizada correctamente',
                'data': {
                    'id': req.id,
                    'request_state': req.request_state,
                    'date_start_production_stage': req.date_start_production_stage,
                    'date_end_production_stage': getattr(req, 'date_end_production_stage', None)
                }
            }

        except RequestAsignation.DoesNotExist:
            return self.error_response('Solicitud no encontrada', 'not_found')
        except Exception as e:
            return self.error_response(f"Error al actualizar la solicitud: {e}", 'update_request_state')


    def create_complete_request_package(self, package_data):
        """Recibe un paquete con estructura:
        {
          'empresa': {...}, 'jefe': {...}, 'talentoHumano': {...}, 'solicitud': {...}
        }
        Crea o usa entidades según 'id' y crea la solicitud en una transacción.
        """
        try:
            # --- Extraer y validar datos antes de crear cualquier objeto ---
            empresa_payload = package_data.get('empresa') or package_data.get('enterprise') or package_data.get('company') or {}
            jefe_payload = package_data.get('jefe') or package_data.get('boss') or {}
            talento_payload = package_data.get('talentoHumano') or package_data.get('human_talent') or {}
            solicitud_payload = package_data.get('solicitud') or package_data.get('request') or {}

            # Map fields from Spanish and English payloads
            apprentice_id = solicitud_payload.get('apprentice') or solicitud_payload.get('aprendiz')
            ficha_id = solicitud_payload.get('ficha') or solicitud_payload.get('cohort')
            fecha_inicio = solicitud_payload.get('fecha_inicio_contrato') or solicitud_payload.get('contract_start_date')
            fecha_fin = solicitud_payload.get('fecha_fin_contrato') or solicitud_payload.get('contract_end_date')
            sede_id = solicitud_payload.get('sede') or solicitud_payload.get('site')
            modality_id = solicitud_payload.get('modality_productive_stage') or solicitud_payload.get('modality')

            if not apprentice_id:
                return self.error_response('El campo solicitud.apprentice es requerido', 'missing_apprentice')

            # Validar existencia de entidades relacionadas antes de crear nada
            apprentice = Apprentice.objects.get(pk=apprentice_id)

            ficha = None
            if ficha_id:
                ficha = Ficha.objects.get(pk=ficha_id)

            sede = None
            if sede_id is not None:
                sede = Sede.objects.get(pk=sede_id)

            modality = None
            if modality_id:
                modality = ModalityProductiveStage.objects.get(pk=modality_id)

            # Validar modalidad y duración
            duracion_meses = 6
            if fecha_inicio and fecha_fin:
                diferencia = relativedelta(fecha_fin, fecha_inicio)
                duracion_meses = diferencia.years * 12 + diferencia.months
                if duracion_meses < 0:
                    return self.error_response("La fecha de fin debe ser posterior a la de inicio.", "invalid_dates")

            try:
                self._validar_solicitud(apprentice_id, ficha_id, modality_id, duracion_meses)
            except Exception as e:
                return self.error_response(str(e), 'validation')

            # --- Si todo es válido, crear objetos dentro de la transacción ---
            with transaction.atomic():
                # Empresa
                if empresa_payload.get('id'):
                    enterprise = Enterprise.objects.get(pk=empresa_payload.get('id'))
                else:
                    name = empresa_payload.get('nombre') or empresa_payload.get('name')
                    nit = empresa_payload.get('nit') or empresa_payload.get('tax_id') or empresa_payload.get('nit_enterprise')
                    locate = empresa_payload.get('direccion') or empresa_payload.get('locate') or empresa_payload.get('address')
                    email = empresa_payload.get('correo') or empresa_payload.get('email') or empresa_payload.get('enterprise_email')
                    enterprise = Enterprise.objects.create(
                        name_enterprise=name or '',
                        nit_enterprise=nit or '',
                        locate=locate or '',
                        email_enterprise=email or ''
                    )

                # Boss
                if jefe_payload.get('id'):
                    boss = Boss.objects.get(pk=jefe_payload.get('id'))
                else:
                    boss = Boss.objects.create(
                        enterprise=enterprise,
                        name_boss=jefe_payload.get('nombre') or jefe_payload.get('name') or '',
                        phone_number=jefe_payload.get('telefono') or jefe_payload.get('phone') or 0,
                        email_boss=jefe_payload.get('correo') or jefe_payload.get('email') or '',
                        position=jefe_payload.get('cargo') or jefe_payload.get('position') or ''
                    )

                # Human Talent
                if talento_payload.get('id'):
                    human_talent = HumanTalent.objects.get(pk=talento_payload.get('id'))
                else:
                    human_talent = HumanTalent.objects.create(
                        enterprise=enterprise,
                        name=talento_payload.get('nombre') or talento_payload.get('name') or '',
                        email=talento_payload.get('correo') or talento_payload.get('email') or '',
                        phone_number=talento_payload.get('telefono') or talento_payload.get('phone') or 0
                    )

                # Actualizar ficha del aprendiz si corresponde
                if ficha_id:
                    apprentice.ficha = ficha
                    apprentice.save()

                request_date_value = fecha_inicio if fecha_inicio else timezone.now().date()

                # Determinar fecha de fin por defecto (6 meses desde la fecha de inicio o request_date)
                if fecha_fin:
                    fecha_fin_value = fecha_fin
                else:
                    base_for_end = fecha_inicio if fecha_inicio else request_date_value
                    fecha_fin_value = base_for_end + relativedelta(months=6)

                request_asignation = RequestAsignation.objects.create(
                    apprentice=apprentice,
                    enterprise=enterprise,
                    modality_productive_stage=modality if modality else ModalityProductiveStage.objects.first(),
                    human_talent=human_talent,
                    boss=boss,
                    request_date=request_date_value,
                    date_start_production_stage=fecha_inicio if fecha_inicio else request_date_value,
                    date_end_production_stage=fecha_fin_value,
                    request_state=RequestState.SIN_ASIGNAR
                )

                # Actualizar PersonSede si se proporcionó sede
                if sede:
                    person = apprentice.person
                    PersonSede.objects.update_or_create(
                        person=person,
                        defaults={"sede": sede}
                    )

                return {
                    'success': True,
                    'message': 'Solicitud creada exitosamente',
                    'data': {
                        'enterprise': {'id': enterprise.id},
                        'boss': {'id': boss.id if boss else None},
                        'human_talent': {'id': human_talent.id if human_talent else None},
                        'request_asignation': {'id': request_asignation.id}
                    }
                }

        except Enterprise.DoesNotExist:
            return self.error_response('Empresa no encontrada', 'not_found')
        except Boss.DoesNotExist:
            return self.error_response('Jefe no encontrado', 'not_found')
        except HumanTalent.DoesNotExist:
            return self.error_response('Talento humano no encontrado', 'not_found')
        except Apprentice.DoesNotExist:
            return self.error_response('Aprendiz no encontrado', 'not_found')
        except Ficha.DoesNotExist:
            return self.error_response('Ficha no encontrada', 'not_found')
        except ModalityProductiveStage.DoesNotExist:
            return self.error_response('Modalidad no encontrada', 'not_found')
        except Exception as e:
            return self.error_response(f"Error al crear solicitud completa: {e}", 'create_complete_request')



    def _validar_solicitud(self, aprendiz_id, ficha_id, modalidad_id, duracion_meses):
        """
        Valida las reglas de negocio para la creación de una solicitud de asignación.
        Lanza ValidationError (o retorna error_response) si alguna regla no se cumple.
        """
        
        solicitudes = RequestAsignation.objects.filter(apprentice_id=aprendiz_id)
        # Estados que NO cuentan como activas
        inactivos = ['RECHAZADA', 'FINALIZADA']
        activas = solicitudes.exclude(request_state__in=inactivos)

        # A. Máximo 2 solicitudes activas
        if activas.count() >= 2:
            raise ValidationError("Solo puedes tener máximo dos solicitudes activas.")

        # B. Misma ficha
        if ficha_id and activas.filter(apprentice__ficha_id=ficha_id).exists():
            raise ValidationError("Ya tienes una solicitud activa con esta ficha.")

        # C. Modalidad contrato
        contrato_nombre = "CONTRATO_APRENDIZAJE"
        modalidad_obj = ModalityProductiveStage.objects.get(pk=modalidad_id) if modalidad_id else None
        if modalidad_obj and modalidad_obj.name_modality.upper().replace(' ', '_') == contrato_nombre:
            if activas.filter(modality_productive_stage__name_modality__iexact=modalidad_obj.name_modality).exists():
                raise ValidationError("Solo puedes tener un contrato de aprendizaje activo.")

        return True