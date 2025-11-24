from core.base.services.implements.baseService.BaseService import BaseService
from apps.assign.repositories.AsignationInstructorRepository import AsignationInstructorRepository
from apps.general.entity.models import Instructor
from apps.assign.entity.models import RequestAsignation
from apps.assign.entity.enums.request_state_enum import RequestState
from apps.assign.entity.models import AsignationInstructor
from apps.security.entity.models import User
from apps.security.emails.AsignacionInstructor import send_instructor_assignment_email
from apps.security.emails.AsignacionInstructor import send_assignment_to_instructor_email
from core.utils.Validation import format_response
from django.db import IntegrityError
from apps.assign.entity.models.Message import Message
from apps.assign.entity.models import VisitFollowing
from dateutil.relativedelta import relativedelta

class AsignationInstructorService(BaseService):
    def __init__(self):
        self.repository = AsignationInstructorRepository()

    def create_custom(self, instructor_id, request_asignation_id, content=None, type_message=None, request_state=None):
        try:
            instructor = Instructor.objects.get(id=instructor_id)
            request_asignation = RequestAsignation.objects.get(id=request_asignation_id)
            # Validar que el estado no sea RECHAZADO
            if request_asignation.request_state == RequestState.RECHAZADO:
                return format_response("No se puede asignar un instructor a una solicitud rechazada.", success=False, type="invalid_state", status_code=400)
            # Validar que el instructor no haya alcanzado su límite máximo de aprendices
            current_learners = instructor.assigned_learners or 0
            max_learners = instructor.max_assigned_learners
            if max_learners is None:
                max_learners = 80
            if max_learners == 0:
                return format_response(
                    "No se pueden asignar aprendices a este instructor porque su límite máximo es 0.",
                    success=False,
                    type="max_learners_zero",
                    status_code=400
                )
            if current_learners >= max_learners:
                return format_response(
                    f"El instructor ha alcanzado su límite máximo de aprendices ({max_learners}). No se pueden asignar más aprendices.",
                    success=False,
                    type="limit_reached",
                    status_code=400
                )
            # Verificar si la solicitud ya tiene una asignación
            existing = AsignationInstructor.objects.filter(request_asignation=request_asignation).first()
            if existing:
                instr = existing.instructor
                instr_name = f"{instr.person.first_name} {instr.person.first_last_name}" if instr and hasattr(instr, 'person') else None
                return format_response(
                    f"La solicitud ya tiene un instructor asignado (id={existing.id}, instructor_id={instr.id if instr else 'N/A'}{', name='+instr_name if instr_name else ''}).",
                    success=False,
                    type="already_assigned",
                    status_code=400
                )

            asignation = self.repository.create_custom(instructor, request_asignation)

            # Si se proporcionó request_state en la petición, validarlo y aplicarlo.
            if request_state:
                valid_states = [choice.value for choice in RequestState]
                if request_state not in valid_states:
                    return format_response(f"Estado inválido. Valores permitidos: {valid_states}", success=False, type="invalid_state", status_code=400)
                request_asignation.request_state = request_state
                request_asignation.save()


            # Validar que no se exceda el máximo de asignaciones
            max_learners = instructor.max_assigned_learners
            if max_learners is None:
                max_learners = 80
            new_assigned_learners = (instructor.assigned_learners or 0) + 1
            if max_learners == 0 or new_assigned_learners > max_learners:
                return format_response(
                    f"No se puede asignar más aprendices. El máximo permitido es {max_learners}.",
                    success=False,
                    type="max_learners_exceeded",
                    status_code=400
                )
            instructor.assigned_learners = new_assigned_learners
            instructor.save()

            # Crear Message asociado si se proporcionó contenido/tipo
            if content or type_message:                
                Message.objects.create(
                    request_asignation=request_asignation,
                    content=content or "",
                    type_message=type_message or ""
                )
            # Enviar correo al aprendiz
            apprentice = request_asignation.apprentice
            person = apprentice.person
            user = User.objects.filter(person=person).first()
            email = user.email if user else None
            if email:
                send_instructor_assignment_email(   
                    email,
                    f"{person.first_name} {person.first_last_name}",
                    f"{instructor.person.first_name} {instructor.person.first_last_name}",
                    person.number_identification,
                    email
                )
            # Enviar correo al instructor asignado
            instructor_user = User.objects.filter(person=instructor.person).first()
            instructor_email = instructor_user.email if instructor_user else None
            if instructor_email:
                send_assignment_to_instructor_email(
                    instructor_email,
                    f"{person.first_name} {person.first_last_name}",
                    f"{instructor.person.first_name} {instructor.person.first_last_name}"
                )
            # Crear visitas automáticas si el estado es 'ASIGNADO'
            if request_asignation.request_state == RequestState.ASIGNADO:
                
                import math
                modality = request_asignation.modality_productive_stage
                start_date = request_asignation.date_start_production_stage
                end_date = request_asignation.date_end_production_stage
                visitas = []
                if modality and start_date:
                    if modality.name_modality.strip().upper().replace(' ', '_') == 'CONTRATO_APRENDIZAJE':
                        fechas = [
                            (1, 'Concertación', start_date + relativedelta(months=1)),
                            (2, 'Visita parcial', start_date + relativedelta(months=3)),
                            (3, 'Visita final', start_date + relativedelta(months=6)),
                        ]
                    elif start_date and end_date:
                        total_days = (end_date - start_date).days
                        if total_days < 1:
                            total_days = 1
                        periodo = total_days / 3
                        fechas = []
                        for i, nombre in enumerate(['Concertación', 'Visita parcial', 'Visita final'], start=1):
                            fecha = start_date + relativedelta(days=round(periodo * (i-1)))
                            fechas.append((i, nombre, fecha))
                    else:
                        fechas = []
                    for num, nombre, fecha in fechas:
                        visitas.append(VisitFollowing(
                            asignation_instructor=asignation,
                            visit_number=num,
                            name_visit=nombre,
                            scheduled_date=fecha,
                            state_visit='por hacer',
                            observations=None,
                            date_visit_made=None,
                            observation_state_visit=None,
                            pdf_report=None
                        ))
                    VisitFollowing.objects.bulk_create(visitas)
            return asignation
        except IntegrityError as ie:
            # Manejo de condición de carrera: si otra petición creó la asignación simultáneamente
            return format_response("La solicitud ya tiene un instructor asignado (concurrency).", success=False, type="already_assigned", status_code=400)
        except Instructor.DoesNotExist:
            return format_response("El instructor no existe.", success=False, type="not_found", status_code=404)
        except RequestAsignation.DoesNotExist:
            return format_response("La solicitud de asignación no existe.", success=False, type="not_found", status_code=404)
        except Exception as e:
            return format_response(f"Error al crear la asignación: {e}", success=False, type="create_custom", status_code=400)
