from rest_framework import serializers
from django.contrib.auth.models import User
from testreport.models import ExtUser


class ExtUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtUser
        fields = ('default_project', 'launches_on_page', 'testresults_on_page')


class AccountSerializer(serializers.ModelSerializer):
    settings = ExtUserSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'date_joined', 'is_active', 'is_staff', 'settings')
        read_only_fields = ('date_joined', )
