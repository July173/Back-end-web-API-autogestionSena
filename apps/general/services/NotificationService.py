from core.base.services.implements.baseService.BaseService import BaseService
from apps.general.repositories.NotificationRepository import NotificationRepository

class NotificationService(BaseService):
    def __init__(self):
        self.repository = NotificationRepository()

    def create_notification(self, validated_data):
        return self.repository.create(**validated_data)

    def list_notifications(self):
        return self.repository.model.objects.all()

    def get_notification(self, pk):
        return self.repository.model.objects.get(pk=pk)
