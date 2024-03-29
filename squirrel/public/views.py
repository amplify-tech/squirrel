from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from . import models
from user.models import *
from login.models import *
import re, csv
from datetime import datetime
import pytz
from django.db.models import Q
utc=pytz.UTC

# Create your views here.

def public_home(request,  user_id=None):
	return render(request, 'public_home.html') 
    
def thatperson(request,  user_id=None):
	who = User.objects.all().filter(id=int(user_id))
	if len(who)!=0:
		srchprsn = who[0]
		profiles = profile.objects.all().filter(owner = srchprsn)
		myprofile = profiles[0]
		return render(request, 'public_profile.html', {'name': srchprsn.username, 'profiles': myprofile}) 
	else:
		return HttpResponse("<h2> url not exist ! </h2> <p> May be this profile is private and you need to Login! </p>")
 


def search(request):
	Alluser = User.objects.all()
	num = len(Alluser)
	name = request.POST['fname']
	prsnid = request.POST['prsnid']
	if len(prsnid) != 0:
		return redirect('/public/' + prsnid)
	elif len(name) != 0:
		query = Q(fullname__icontains=name)
		query.add(Q(bio__icontains=name), Q.OR)
		query.add(Q(school__icontains=name), Q.OR)
		query.add(Q(hometown__icontains=name), Q.OR)
		query.add(Q(livesin__icontains=name), Q.OR)

		profilelist = profile.objects.all().filter(query)

		if len(profilelist)==0:
			messages.info(request, 'Person with this info not found')
			return render(request, 'home.html' , {'numuser' : num})
		else:
			return render(request, 'public_home.html', {'profilelist': profilelist}) 
	else:
		return render(request, 'home.html' , {'numuser' : num})

