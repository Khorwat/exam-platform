from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user', 'notification_type', 'title', 'message', 
                  'is_read', 'related_exam_id', 'created_at')
        read_only_fields = ('id', 'created_at', 'user')

