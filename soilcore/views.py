from django.shortcuts import render

def loginsignuppage(request):
    return render(request, 'log_sign.html')
def homepage(request):
    return render(request, 'home.html')
def navbar(request):
    return render(request, 'nav.html')