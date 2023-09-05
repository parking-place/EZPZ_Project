from django.urls import path

from .views import review_page, review_quart

urlpatterns = [
    path('', review_page, name='review-page'),
    path('half', review_page, name='review-page'),
    path('quarter', review_quart, name='review-quart')
]
