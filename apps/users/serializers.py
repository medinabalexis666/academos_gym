from rest_framework import serializers
from .models import CustomUser 


class UserSerializer(serializers.ModelSerializer):
    #para poder hacer CRUD
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser 
        fields = ('id', 'nombre', 'email', 'password', 'is_active')

    def create(self, validated_data):
        password = validated_data.pop('password')
        return CustomUser.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        if password:
            instance.set_password(password)
        instance.save()
        return instance