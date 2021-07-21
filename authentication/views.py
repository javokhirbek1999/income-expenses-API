import jwt, os
from django.http import request
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect

from rest_framework import status, generics, views, permissions
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from .serializers import UserSerializer, EmailVerificationSerializer, LoginAPISerializer, RequestPasswordResetEmailSerializer,SetNewPasswordSerializer, LogoutSerializer
from .models import User
from .utils import Util
from .renderers import UserRenderer


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEMA'),'http','https']


class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])
        token=RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('email_verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = f"Hi {user.username}!\nPlease click on the link below to confirm your account \n {absurl}"
        data = {'email_body':email_body, 'to_email':user.email, 'email_subject':'Verify your account'}

        Util.send_mail(data)
        
        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):

    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description="Enter verification token", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
    
        token = request.GET.get('token')
        print(token)
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'status':'Email is successfully activated'}, status=status.HTTP_201_CREATED)
        except jwt.ExpiredSignatureError:
            return Response({'status':'Activation link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'status':'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginAPISerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token=PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            redirect_url = request.data.get('redirect_url','')
            absurl = 'http://'+current_site+relativeLink
            email_body = 'Hello !\n Use the link below to reset your password'+absurl+'?redirect_url='+redirect_url
            data = {'email_body':email_body,'to_email':user.email, 'email_subject':'Reset your password'}

            Util.send_mail(data)

        return Response({'success':'We have sent you the link to reset your password'},status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):


    def get(self,request,uidb64,token):
        redirect_url = request.GET.get('redirect_url')
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user,token):

                if len(redirect_url)>3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL','')+'?token_valid=False')

            if redirect_url and len(redirect_url)>3:
                return CustomRedirect(redirect_url+'?token_valid=True&?message=Credentials are valid?&uidb64='+uidb64+'token='+token)
            
        except DjangoUnicodeDecodeError as e:
            if not PasswordResetTokenGenerator().check_token(user):
                return CustomRedirect(redirect_url+'?token_valid=False')



class SetNewPasswordAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True,'message':'Password reset successful'},status=status.HTTP_200_OK)
        
class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthUserAPIView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request):
        user = User.objects.get(pk=request.user.pk)
        serializer = UserSerializer(user)

        return Response(serializer.data)