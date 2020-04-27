from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
from user.models import *
from login.models import *
from django.contrib.auth.models import User, auth
from django.contrib import messages
# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return redirect('/user/' +str(request.user.id))
    else:
        all_users = User.objects.all()
        num = len(all_users)
        return render(request, 'home.html' , {'numuser' : num})

def login(request):
    if request.method == 'POST':
        username = request.POST['fname']
        paswd = request.POST['pswd']

        user = auth.authenticate(username=username, password=paswd)

        if user is not None:
            auth.login(request,user)
            myprofile = profile.objects.all().filter(owner = user)[0]
            myprofile.isactive = True
            myprofile.save()
            return redirect('/user/' +str(user.id))
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('/login')

    else:
        return render(request, 'login.html')
        

def register(request):
    if request.method == 'POST':
        username = request.POST['fname']
        fullname = request.POST['fullname']
        passwd = request.POST['pswd']

        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username Taken')
            return redirect('register')
        else:
            user = User.objects.create_user(username=username,first_name=fullname ,password=passwd)
            user.save()
            print("proflie created")
            newprofile = profile(owner=user , fullname=fullname)
            newprofile.save()
            return redirect('login')

    else:
        return render(request, 'register.html')

def logout(request):
    user = request.user
    myprofile = profile.objects.all().filter(owner = user)[0]
    myprofile.isactive = False
    myprofile.save()
    auth.logout(request)
    return redirect('/')
