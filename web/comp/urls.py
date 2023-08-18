from django.urls import path

from .views import comp

urlpatterns = [
    path('', comp, name='comp')
]
