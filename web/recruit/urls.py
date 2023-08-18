from django.urls import path

from .views import recruit_page

urlpatterns = [
    path('', recruit_page, name='recruit-page')
]
