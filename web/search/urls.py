from django.urls import path, include

from .views import main_page


urlpatterns = [
    path('', main_page, name='main-page'),
]
