from rest_framework import serializers
from core.models import User
from django.urls import reverse


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["url", "first_name", "last_name"]

    def get_url(self, obj: User) -> str:
        request = self.context["request"]
        return (
            request.protocol
            + request.get_host()
            + reverse("core:user_details", args=[obj.username])
        )
