from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.general.entity.models.Notification import Notification
from apps.general.entity.serializers.NotificationSerializer import NotificationSerializer
from apps.general.services.NotificationService import NotificationService

class NotificationViewset(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    service_class = NotificationService

    @action(detail=False, methods=['post'], url_path='create')
    def create_notification(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = self.service_class().create_notification(serializer.validated_data)
        return Response(self.get_serializer(notification).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='list')
    def list_notifications(self, request):
        notifications = self.service_class().list_notifications()
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='get')
    def get_notification(self, request, pk=None):
        notification = self.service_class().get_notification(pk)
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
