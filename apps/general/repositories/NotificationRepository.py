from core.base.repositories.implements.baseRepository.BaseRepository import BaseRepository
from apps.general.entity.models.Notification import Notification

class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

    def create_notification(self, **validated_data):
        return self.model.objects.create(**validated_data)

    def list_notifications(self):
        return self.model.objects.all()

    def get_notification(self, pk):
        return self.model.objects.get(pk=pk)
