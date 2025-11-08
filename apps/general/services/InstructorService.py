from apps.security.services.PersonService import PersonService
from apps.security.services.UserService import UserService
from apps.security.entity.models.DocumentType import DocumentType
from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.InstructorRepository import InstructorRepository
from django.db import transaction
from apps.general.entity.models import Sede, KnowledgeArea, TypeContract
from apps.security.entity.models import User, Person
from apps.general.entity.models import Instructor
from core.utils.Validation import is_unique_email, validate_document_number, validate_phone_number, format_response
from core.utils.Validation import is_sena_email
from django.contrib.auth.hashers import make_password
from apps.security.emails.CreacionCuentaUsers import send_account_created_email


class InstructorService(BaseService):
    def update_learners_fields(self, instructor_id, assigned_learners=None, max_assigned_learners=None):
        instructor = Instructor.objects.filter(pk=instructor_id).first()
        if not instructor:
            return None
        # Validación: assigned_learners nunca menor que 0
        if assigned_learners is not None:
            if assigned_learners < 0:
                raise ValueError('El número de aprendices asignados no puede ser menor que 0.')
            # Validación: no superar el límite
            max_limit = max_assigned_learners if max_assigned_learners is not None else instructor.max_assigned_learners or 80
            if assigned_learners > max_limit:
                raise ValueError('El número de aprendices asignados no puede superar el límite máximo.')
            instructor.assigned_learners = assigned_learners
        if max_assigned_learners is not None:
            if max_assigned_learners < 0:
                raise ValueError('El límite máximo no puede ser menor que 0.')
            instructor.max_assigned_learners = max_assigned_learners
            # Si el límite se reduce por debajo de los asignados, ajusta los asignados
            if instructor.assigned_learners is not None and instructor.assigned_learners > max_assigned_learners:
                instructor.assigned_learners = max_assigned_learners
        instructor.save()
        return instructor

    def __init__(self):
        self.repository = InstructorRepository()

    def list_instructors(self):
        """
        Devuelve todos los instructores.
        """
        return Instructor.objects.all()


    def create_instructor(self, person_data, user_data, instructor_data, sede_id):
        try:
            # Validaciones previas
            email = user_data.get('email')
            numero_identificacion = person_data.get('number_identification')
            phone_number = person_data.get('phone_number')
            contract_type_id = instructor_data.get('contract_type_id') or instructor_data.get('contract_type')
            knowledge_area_id = instructor_data.get('knowledge_area_id') or instructor_data.get('knowledge_area')

            if not is_sena_email(email):
                return format_response('Solo se permiten correos institucionales (@sena.edu.co) para instructores.', success=False, type='invalid_email', status_code=400)
            if not is_unique_email(email, User):
                return format_response('El correo institucional ya está registrado.', success=False, type='email_exists', status_code=400)
            valid_doc, doc_msg = validate_document_number(numero_identificacion, Person)
            if not valid_doc:
                return format_response(doc_msg, success=False, type='invalid_document', status_code=400)
            if phone_number:
                valid_phone, phone_msg = validate_phone_number(phone_number)
                if not valid_phone:
                    return format_response(phone_msg, success=False, type='invalid_phone', status_code=400)

            if not contract_type_id:
                return format_response('El tipo de contrato es obligatorio.', success=False, type='invalid_contract_type', status_code=400)
            if not knowledge_area_id:
                return format_response('El área de conocimiento es obligatoria.', success=False, type='invalid_knowledge_area', status_code=400)
            try:
                sede = Sede.objects.get(pk=sede_id)
            except Sede.DoesNotExist:
                return format_response('La sede proporcionada no existe.', success=False, type='invalid_sede', status_code=400)
            try:
                contract_type = TypeContract.objects.get(pk=contract_type_id)
            except Exception:
                return format_response('El tipo de contrato proporcionado no existe.', success=False, type='invalid_contract_type', status_code=400)
            try:
                knowledge_area = KnowledgeArea.objects.get(pk=knowledge_area_id)
            except Exception:
                return format_response('El área de conocimiento proporcionada no existe.', success=False, type='invalid_knowledge_area', status_code=400)

            # Validate TypeIdentification
            type_id = person_data.get('type_identification')
            if type_id and not isinstance(type_id, DocumentType):
                person_data['type_identification'] = DocumentType.objects.get(pk=type_id)
                
            
            #Transactional handling of data creation
            with transaction.atomic():
                # 1. Create person
                person = PersonService().create(person_data)
                if isinstance(person, dict) and person.get('status') == 'error':
                    raise Exception(person.get('message', 'No se pudo crear la persona'))

                user_data['person_id'] = person.id
                
                # 2. Create user
                # Activate user automatically
                user_data['is_active'] = True
                # Allow dynamic role
                if 'role_id' not in user_data:
                    return format_response('El rol es obligatorio.', success=False, type='invalid_role', status_code=400)
                # Hash the password using the identification number
                from django.utils.crypto import get_random_string
                identification_number = str(person_data.get('number_identification'))
                temp_suffix = get_random_string(length=2)
                temp_password = identification_number + temp_suffix
                user_data['password'] = temp_password
                user = UserService().create(user_data)
                if isinstance(user, dict) and user.get('status') == 'error':
                    raise Exception(user.get('message', 'No se pudo crear el usuario'))

                # 3. Create instructor
                instructor_data['person'] = person
                instructor_data['contract_type'] = contract_type
                instructor_data['knowledge_area'] = knowledge_area
                instructor = Instructor.objects.create(**instructor_data)
                
                # 4. Send account creation email to instructor
                full_name = f"{person.first_name} {person.first_last_name}"
                send_account_created_email(user.email, full_name, temp_password)
                # 4. Serialize response
                return format_response(
                    "Instructor registrado correctamente.",
                    success=True,
                    type='register_instructor',
                    status_code=201
                )
        except Exception as e:
            return format_response(str(e), success=False, type='register_instructor', status_code=400)

    def update_instructor(self, instructor_id, person_data, user_data, instructor_data, sede_id):
        with transaction.atomic():
            instructor = Instructor.objects.get(pk=instructor_id)
            # Convierte el ID en instancia si existe en instructor_data
            if 'knowledgeArea' in instructor_data:
                knowledge_area_id = instructor_data.pop('knowledgeArea')
                instructor_data['knowledgeArea'] = KnowledgeArea.objects.get(pk=knowledge_area_id)

            # Manejar nuevos campos opcionales
            assigned_learners = instructor_data.pop('assigned_learners', None)
            max_assigned_learners = instructor_data.pop('max_assigned_learners', 80)
            instructor_data['assigned_learners'] = assigned_learners
            instructor_data['max_assigned_learners'] = max_assigned_learners

            # Obtener el usuario usando el objeto Person vinculado al Instructor
            person = instructor.person
            user = User.objects.filter(person=person).first()

            # Validaciones reutilizables para update (excluyendo el usuario actual)
            if not is_unique_email(user_data['email'], User, exclude_user_id=user.id if user else None):
                raise ValueError('El correo ya está registrado.')
            # Permitir que el número de identificación sea el mismo que el actual
            if int(person_data['number_identification']) != int(person.number_identification):
                if not validate_document_number(person_data['number_identification'], Person, exclude_person_id=person.id):
                    raise ValueError('El número de documento ya está registrado.')
            # Validación de número de teléfono
            if person_data.get('phone_number') and not validate_phone_number(person_data['phone_number']):
                raise ValueError('El número de teléfono debe tener exactamente 10 dígitos.')

            self.repository.update_all_dates_instructor(
                instructor,
                person_data,
                user_data,
                instructor_data,
                sede_id=sede_id
            )
            return {
                "person_id": person.id,
                "user_id": user.id if user else None,
                "instructor_id": instructor.id,
                "sede_id": sede_id
            }
