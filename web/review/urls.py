from django.urls import path

from .views import review_page

urlpatterns = [
    path('', review_page, name='review-page')
]
