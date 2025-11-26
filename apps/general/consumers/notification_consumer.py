import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.general.entity.models.Notification import Notification
from apps.general.entity.serializers.NotificationSerializer import NotificationSerializer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Opcional: manejar mensajes entrantes del cliente
        pass

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps(notification))

    @database_sync_to_async
    def get_user_notifications(self):
        notifications = Notification.objects.filter(id_user_id=self.user_id, is_read=False)
        return NotificationSerializer(notifications, many=True).data
