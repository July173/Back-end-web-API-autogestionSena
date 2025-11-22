from apps.assign.entity.models import Message


class MessageRepository:
    def get(self):
        """Return all Message records."""
        return Message.objects.all()

    def get_by_id(self, pk):
        """Return a single Message by primary key or None if not found."""
        try:
            return Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            return None

    def create(self, request_asignation, content, type_message):
        """Create and return a new Message instance."""
        return Message.objects.create(
            request_asignation=request_asignation,
            content=content,
            type_message=type_message
        )
        
    def update_request_state(self, message_id, request_state):
        """Actualiza solo el estado de la solicitud asociada a un mensaje."""
        from apps.assign.entity.models import Message
        try:
            message = Message.objects.get(pk=message_id)
            message.request_asignation.request_state = request_state
            message.request_asignation.save()
            return message
        except Message.DoesNotExist:
            return None
