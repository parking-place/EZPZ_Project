from django.shortcuts import render

# Create your views here.
def review_page(request):
    return render(request, 'review/review.html')
