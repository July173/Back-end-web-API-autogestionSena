from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.ProgramRepository import ProgramRepository
from apps.general.entity.models import Program



class ProgramService(BaseService):
    def get_filtered_programs(self, active=None, search=None):
        queryset = Program.objects.all()
        if active is not None:
            if str(active).lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(active=True)
            elif str(active).lower() in ['false', '0', 'no']:
                queryset = queryset.filter(active=False)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def __init__(self):
        self.repository = ProgramRepository()

    def get_fichas_by_program(self, program_id):
        """
        Devuelve las fichas vinculadas a un programa específico.
        """
        return self.repository.get_fichas_by_program(program_id)
    
    def logical_delete_program(self, program_id):
        """
        Realiza borrado lógico o reactivación de programa y sus fichas vinculadas.
        """
        program = self.get(program_id)
        if not program:
            raise ValueError(f"Programa con ID {program_id} no encontrado")
        if not program.active:
            self.repository.set_active_state_program_with_fichas(program_id, active=True)
            return "Programa reactivado correctamente."
        else:
            self.repository.set_active_state_program_with_fichas(program_id, active=False)
            return "Eliminación lógica realizada correctamente."
