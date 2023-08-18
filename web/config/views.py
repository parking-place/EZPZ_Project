from django.shortcuts import render

def main_page(request):
    return render(request, 'main.html')

def comp(request):
    return render(request, 'comp.html')
