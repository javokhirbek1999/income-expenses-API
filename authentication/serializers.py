from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    
    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('Username must be alphanumeric')
        
        return attrs
    
    def create(self, validated_data):
       return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginAPISerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True, style={'input_type':'password'})
    username = serializers.CharField(max_length=255, min_length=6, read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self,obj):
        user = User.objects.get(email=obj['email'])

        return {
            'acccess':user.tokens()['access'],
            'refresh':user.tokens()['refresh']
        }

    class Meta:
        model = User
        fields = ['email','username','password','tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = authenticate(email=email,password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('User is disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

        return super().validate(attrs)

class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=6)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6,max_length=68,write_only=True)
    token = serializers.CharField(min_length=1,write_only=True)
    uidb64 = serializers.CharField(min_length=1,write_only=True)

    class Meta:
        fields = ['password','token','uidb64']


    def validate(self,attrs):
        try:
            password=attrs.get('password')
            token=attrs.get('token')
            uidb64=attrs.get('uidb64')

            id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed('The reset token is invalid',401)

            user.set_password(password)
            user.save()
        except Exception as e:
            raise AuthenticationFailed('The reset token link is invalid',401)
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token':('Token is invalid or expired')
    }

    def validate(self,attrs):
        self.token = attrs['refresh']

        return attrs


    def save(self,**kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')