from django.urls import path

from .views import review_half, review_quarter

urlpatterns = [
    path('', review_half, name='review-page'),
    path('half', review_half, name='review-page'),
    path('quarter', review_quarter, name='review-quart')
]
