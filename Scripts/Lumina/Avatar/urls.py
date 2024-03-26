from django.urls import path
from Avatar.views import test

urlpatterns = [
    path('', test),
]