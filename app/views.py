from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from .serializers import *
from .models import *


class AllPlacesView(ListAPIView):
    queryset = PlaceModel.objects.all()
    serializer_class = MultiPlacesModelSerializer


class SinglePlaceView(RetrieveAPIView):
    queryset = PlaceModel.objects.all()
    serializer_class = SinglePlaceModelSerializer
    lookup_field = "id"

