from django.shortcuts import render


def home_view(request):
    user = request.user
    return render(request, 'home/mainpage.html',{'user': user})

