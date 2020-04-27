from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import *
import re, csv
from datetime import datetime
import pytz
from .forms import *

utc=pytz.UTC

def dashboard(request,  user_id=None):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            form = Prof_form()
            status_form = Status_form()
            pictures = Profile_pic.objects.all().filter(owner=request.user).last()
            status = Status.objects.all().filter(owner=request.user).order_by('-id')
            return render(request, 'profile.html', {'profile':myprofile, 'form' : form,  'status_form' : status_form, 'pimages' : pictures, 'status':status}) 

        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')




def chat(request,  user_id=None , ricvr_id=None) :
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')

    elif request.user.is_authenticated:
        user = request.user
        myprofile = profile.objects.get(owner = user)
        total_notify = myprofile.all_notify
        if ricvr_id == "0":
            return render(request, 'chat.html', {'all_notify':total_notify})
        else:
            # now he is reading msz so remove some notification

            ricvr = User.objects.get(id=int(ricvr_id))
            thischat_key =  str(min(user.id, int(ricvr_id))) + "@" + str(max(user.id, int(ricvr_id)))

            oldchat = Chate.objects.all().filter(chatkey=thischat_key)
            # notifiction  --n     ********************************
            n1 = 0
            n2 = 0 
            # following
            flwing = User_Following.objects.all().filter(user_id=user.id, following=ricvr)
            if len(flwing) != 0:
                flwing1 = flwing[0]
                n1 = flwing1.notification
                flwing1.notification = 0
                flwing1.save()
                print("all mszs readed of flwing1")

            # followers
            flwer = User_Follower.objects.all().filter(user_id=user.id, follower=ricvr)
            if len(flwer) != 0:
                flwer1 = flwer[0]
                n2 = flwer1.notification
                flwer1.notification = 0
                flwer1.save()
                print("all mszs readed of flwer1")

            # all notify**********************
            myprofile.all_notify = myprofile.all_notify - max(n1, n2)   #hopefully n1=n2
            myprofile.save()

            total_notify2 = myprofile.all_notify
            print("some msz readed from all notify")
            # **************************************************

            return render(request, 'chat.html', {'ourchat': oldchat, 'rcvr': ricvr, 'rcvr_id':ricvr_id, 'all_notify':total_notify2, 'chat_key':thischat_key})
    else:
        messages.info(request, 'Please Login First')
        return render(request, 'login.html')

def myfrnd(request,  user_id=None) :
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            total_notify = myprofile.all_notify
            
            # following
            flwing = User_Following.objects.all().filter(user_id=user.id)
            profile_flwing=[]
            for i in flwing:
                hisprofile = profile.objects.get(owner = i.following)
                profile_flwing.append([i , hisprofile])

            # follower       list of pair 
            flwer = User_Follower.objects.all().filter(user_id=user.id)
            profile_flwer=[]
            for i in flwer:
                himprofile = profile.objects.get(owner = i.follower)
                profile_flwer.append([i , himprofile])

            return render(request, 'myfrnd.html', { 'allfollowing': profile_flwing, 'allfolower': profile_flwer, 'all_notify':total_notify})
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')

def findfrnd(request,  user_id=None) :
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            total_notify = myprofile.all_notify
            myflwing = User_Following.objects.all().filter(user_id=user.id)
            all_users = User.objects.all().exclude(username=user.username)
            for f in myflwing:
                all_users=all_users.exclude(username=f.following.username)   
                 #remove those are already  following
            all_users = all_users.order_by('username')
            return render(request, 'findfrnd.html', {'alluser': all_users, 'all_notify':total_notify})
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')

def saveprofile(request,user_id=None ):
    print("**************saved profile***********")
    user = request.user
    myprofile = profile.objects.get(owner = user)

    bio = request.POST['bio']
    livesin = request.POST['livesin']
    hometown = request.POST['hometown']
    school = request.POST['school']
    fullname = request.POST['fullname']

    myprofile.bio = bio
    myprofile.livesin = livesin
    myprofile.hometown = hometown
    myprofile.school = school
    myprofile.save()

    user.first_name = fullname
    user.save()
    return redirect('/user/' +str(user.id))

def following(request,user_id=None ):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.all().filter(owner = request.user)[0]
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            ideal_user_id = request.POST['userid']
            ideal_user = User.objects.get(id=int(ideal_user_id))

            # following **************************************************
            newflwing = User_Following(user_id = user.id, following = ideal_user, notification=0)
            newflwing.save()
            
            # # follower ***************************************************
            newflwr = User_Follower(user_id = ideal_user.id, follower = user, notification=0)
            newflwr.save()

            return redirect('/user/' +str(user.id) + '/findfrnd')
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')


def startchat(request,user_id=None ):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.all().filter(owner = request.user)[0]
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            whom = request.POST['userid']

            return redirect('/user/' +str(user.id) + '/chat/' +str(whom))
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')

def delete_flwing(request,user_id=None ):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            whom = request.POST['flwing_del_id']
            his_profile = profile.objects.get(owner = int(whom))

            flwinglist = User_Following.objects.filter(user_id=user.id, following=int(whom))
            if len(flwinglist) !=0:
                myprofile.all_notify =myprofile.all_notify -  flwinglist[0].notification
                flwinglist.delete()

            flwerlist = User_Follower.objects.filter(user_id=int(whom), follower=user.id)
            if len(flwerlist) !=0:
                his_profile.all_notify =his_profile.all_notify -  flwerlist[0].notification
                flwerlist.delete()

            myprofile.save()
            his_profile.save()

            return redirect('/user/' +str(user.id) + '/myfrnd')
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')

def delete_flwer(request,user_id=None ):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            whom = request.POST['flwer_del_id']

            myprofile = profile.objects.get(owner = user)
            his_profile = profile.objects.get(owner = int(whom))

            flwerlist = User_Follower.objects.filter(user_id=user.id, follower=int(whom))
            if len(flwerlist) !=0:
                myprofile.all_notify =myprofile.all_notify -  flwerlist[0].notification
                flwerlist.delete()

            flwinglist = User_Following.objects.filter(user_id=int(whom), following=user.id)
            if len(flwinglist) !=0:
                his_profile.all_notify =his_profile.all_notify -  flwinglist[0].notification
                flwinglist.delete()

            myprofile.save()
            his_profile.save()

            return redirect('/user/' +str(user.id) + '/myfrnd')
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')


def chat_del(request,user_id=None,  ricvr_id=None):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            thischat_key = request.POST['chate_key_del']

            chatdel = Chate.objects.all().filter(chatkey = thischat_key).delete()

            return redirect('/user/' +str(user.id) + '/chat/' + str(ricvr_id))
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')

def prof_del(request,user_id=None,  ricvr_id=None):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.get(owner = request.user)
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            profile.objects.all().filter(owner = user).delete()
            Chate.objects.all().filter(sender= user).delete()
            User_Following.objects.all().filter(user_id= user.id).delete()
            User_Following.objects.all().filter(following= user).delete()
            User_Follower.objects.all().filter(user_id= user.id).delete()
            User_Follower.objects.all().filter(follower= user).delete()
            Profile_pic.objects.all().filter(owner= user).delete()
            Status.objects.all().filter(owner= user).delete()
            User.objects.all().filter(username= user.username).delete()

            return render(request, 'home.html')
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')


def viewprofile(request,user_id=None, ricvr_id=None ):
    if int(user_id) != request.user.id:
        myprofile = profile.objects.all().filter(owner = request.user)[0]
        myprofile.isactive = False
        myprofile.save()
        auth.logout(request)
        messages.info(request, 'you entered wrong url')
        return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            user = request.user
            # who_id = request.POST['userid_view']
            whose_user = User.objects.get(id=int(ricvr_id))
            whose_profile = profile.objects.get(owner=whose_user)
            status = Status.objects.all().filter(owner=whose_user).order_by('-id')
            pictures = Profile_pic.objects.all().filter(owner=whose_user).last()
            num_flwing= User_Following.objects.all().filter(user_id=int(ricvr_id)).count()
            num_flwer= User_Follower.objects.all().filter(user_id=int(ricvr_id)).count()

            return render(request, 'viewprofile.html' , {'whose_profile' :whose_profile, 'status':status, 'pimages':pictures, 'num_flwing':num_flwing, 'num_flwer':num_flwer})
        else:
            messages.info(request, 'Please Login First')
            return render(request, 'login.html')


def submitted(request,user_id=None):
    print("**************submit***********")
    user = request.user
    rcvr = request.POST['rcvr']
    curmsz = request.POST['mymsz']
    newstr = curmsz
    print(curmsz)

    if len(newstr.strip()) == 0:
        return redirect('/user/' + str(user.id) + '/chat/' +str(rcvr)+ "#rcvridd")
    else:
        # notifiction  +1     ********************************
        # following
        flwing = User_Following.objects.all().filter(user_id=int(rcvr), following=user)
        if len(flwing) != 0:
            flwing1 = flwing[0]
            flwing1.notification = flwing1.notification + 1
            flwing1.save()

        # followers
        flwer = User_Follower.objects.all().filter(user_id=int(rcvr), follower=user)
        if len(flwer) != 0:
            flwer1 = flwer[0]
            flwer1.notification = flwer1.notification + 1
            flwer1.save()
        # all notify**********************

        user_ricvr = User.objects.get(id=int(rcvr))
        rcvr_profile = profile.objects.get(owner = user_ricvr)
        rcvr_profile.all_notify =  rcvr_profile.all_notify  + 1
        rcvr_profile.save()
        # **************************************************

        thischat_key =  str(min(user.id, int(rcvr))) + "@" + str(max(user.id, int(rcvr)))
        
        msz1 = Chate(sender=user, chatkey=thischat_key, msz=curmsz)
        msz1.save()
        return redirect('/user/' + str(user.id) + '/chat/' +str(rcvr) + "#rcvridd")



def update_pic(request, user_id=None): 
    if request.method == 'POST': 
        form = Prof_form(request.POST, request.FILES) 
        if form.is_valid():
            Profile_pic.objects.filter(owner=request.user).delete()
            temp = form.save(commit=False) 
            temp.owner = request.user
            temp.save()

            # return redirect('success') 
    else: 
        form = Prof_form()
    return redirect('/user/' +str(request.user.id))


def update_status(request, user_id=None): 
    if request.method == 'POST': 
        form = Status_form(request.POST, request.FILES) 
        if form.is_valid(): 
            temp = form.save(commit=False) 
            temp.owner = request.user
            temp.save()

            # return redirect('success') 
    else: 
        form = Status_form()
    return redirect('/user/' +str(request.user.id))


def likes(request, user_id=None):
    status_id = request.POST['status_id']

    oldlike, newlike = Likes.objects.get_or_create(status_id=int(status_id), who_like=request.user)

    if newlike:
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like +=1
        the_status.save()

    else:
        oldlike.delete()
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like -=1
        the_status.save()

    return redirect('/user/' +str(request.user.id) + '#' + str(status_id))

def other_likes(request, user_id=None, ricvr_id=None ):
    status_id = request.POST['status_id']

    oldlike, newlike = Likes.objects.get_or_create(status_id=int(status_id), who_like=request.user)

    if newlike:
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like +=1
        the_status.save()

    else:
        oldlike.delete()
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like -=1
        the_status.save()

    return redirect('/user/' +str(request.user.id) + "/viewprofile/"+ str(ricvr_id) + "#" + str(status_id))


def del_status(request, user_id=None):
    status_id = request.POST['status_id']
    
    the_status = Status.objects.get(id=int(status_id))
    the_status.delete()
    Likes.objects.filter(status_id=int(status_id)).delete()

    return redirect('/user/' +str(request.user.id) + '#' + str("posts"))

def del_prof_pic(request, user_id=None):
    Profile_pic.objects.all().filter(owner=request.user).delete()

    return redirect('/user/' +str(request.user.id))



# imp ++++++++++++++**********++++++++++
# id = 'some identifier'
# person, created = Person.objects.get_or_create(identifier=id)

# if created:
#    # means you have created a new person
# else:
#    # person just refers to the existing one
