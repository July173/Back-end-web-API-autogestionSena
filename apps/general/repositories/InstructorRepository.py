from django.db.models import Q
from apps.security.entity.models import Person, User
from apps.security.entity.models.DocumentType import DocumentType
from core.base.repositories.implements.baseRepository.BaseRepository import BaseRepository
from apps.general.entity.models import Instructor, PersonSede, Sede
from django.db import transaction

class InstructorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Instructor)
    
    def get_filtered_instructors(self, search=None, knowledge_area_id=None):
        queryset = self.model.objects.select_related('person', 'knowledgeArea').all()
        if search:
            queryset = queryset.filter(
                Q(person__first_name__icontains=search) |
                Q(person__second_name__icontains=search) |
                Q(person__first_last_name__icontains=search) |
                Q(person__second_last_name__icontains=search) |
                Q(person__number_identification__icontains=search)
            )
        if knowledge_area_id:
            queryset = queryset.filter(knowledgeArea__id=knowledge_area_id)
        return list(queryset)


    def update_all_dates_instructor(self, instructor, person_data, user_data, instructor_data, sede_id=None):
        """
        Actualiza persona, usuario, instructor y person_sede en una sola transacción.
        """
        with transaction.atomic():
            # Persona
            for attr, value in person_data.items():
                setattr(instructor.person, attr, value)
            instructor.person.save()
            # Usuario
            user = User.objects.filter(person=instructor.person).first()
            if user:
                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()
            # Instructor
            for attr, value in instructor_data.items():
                setattr(instructor, attr, value)
            instructor.save()
            # PersonSede
            if sede_id:
                sede_instance = Sede.objects.get(pk=sede_id)
                person_sede = PersonSede.objects.filter(PersonId=instructor.person).first()
                if person_sede:
                    person_sede.SedeId = sede_instance
                    person_sede.save()
            return instructor
