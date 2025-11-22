from rest_framework import serializers
from apps.assign.entity.models.Message import Message

class MessageAsignationSerializer(serializers.ModelSerializer):
	request_asignation = serializers.PrimaryKeyRelatedField(queryset=Message._meta.get_field('request_asignation').related_model.objects.all())
	request_state = serializers.CharField(source='request_asignation.request_state', read_only=True)

	class Meta:
		model = Message
		fields = ['id', 'request_asignation', 'content', 'type_message', 'request_state']
    