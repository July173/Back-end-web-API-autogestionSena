from apps.general.entity.models.Notification import Notification


class NotificationRepository:
    def __init__(self):
        self.model = Notification

    def list_all(self):
        """Devuelve todas las notificaciones ordenadas por fecha descendente."""
        return self.model.objects.all().order_by('-created_at')


    def get_by_apprentice_id(self, apprentice_id):
        """Devuelve notificaciones del usuario con rol 'Aprendiz'."""
        return self.model.objects.filter(
            id_user__id=apprentice_id,
            id_user__role__type_role__iexact='Aprendiz'
        ).order_by('-created_at')


    def get_by_instructor_id(self, instructor_id):
        """Devuelve notificaciones del usuario con rol 'Instructor'."""
        return self.model.objects.filter(
            id_user__id=instructor_id,
            id_user__role__type_role__iexact='Instructor'
        ).order_by('-created_at')

    def get_by_coordinator_id(self, coordinator_id):
        """Devuelve notificaciones del usuario con rol 'Coordinador'."""
        return self.model.objects.filter(
            id_user__id=coordinator_id,
            id_user__role__type_role__iexact='Coordinador'
        ).order_by('-created_at')

    def get_by_admin_id(self, admin_id):
        """Devuelve notificaciones del usuario con rol 'Administrador'."""
        return self.model.objects.filter(
            id_user__id=admin_id,
            id_user__role__type_role__iexact='Administrador'
        ).order_by('-created_at')

    def get_by_sofia_operator_id(self, sofia_operator_id):
        """Devuelve notificaciones del usuario con rol 'Operador Sofia Plus'."""
        return self.model.objects.filter(
            id_user__id=sofia_operator_id,
            id_user__role__type_role__iexact='Operador Sofia Plus'
        ).order_by('-created_at')

