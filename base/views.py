from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message,User
from .forms import RoomForm,UserForm,RegistrationForm,LogInForm
from django.contrib.auth.forms import PasswordChangeForm
import re
# from django.contrib.auth.forms import PasswordChangeFor
from .utils import get_user_from_email_verification_token, send_email_verification

# Create your views here.

# rooms = [
#   {"id": 1,"name": "Mustang learning"},
#   {"id": 2,"name": "toyotaz learning"},
#   {"id": 3,"name": "benzzzz learning"}
# ]

#USER REGISTRATION
def register(request):
    #if request is a get request return user registration form
    if request.method=="GET":
        form=RegistrationForm()
        return render(request,'base/login_register.html',{'form':form})

    #if request is a post request create user
    elif request.method=="POST":
        filled_form=RegistrationForm(request.POST)
        #check if form is valid
        if filled_form.is_valid():

            first_name=filled_form.cleaned_data['first_name']
            # last_name=filled_form.cleaned_data['last_name']
            username=filled_form.cleaned_data['username']
            email=filled_form.cleaned_data['email']
            password=filled_form.cleaned_data['password']
             
            #create new user
            new_user = User.objects.create(
                first_name=first_name,
                # last_name=last_name,
                username=username,
                email=email,
                password=password,
                is_active = False
                )
            
            if send_email_verification(request=request, user = new_user):
                return redirect('login')
            else:
                new_user.delete()
                return redirect('register')

        #if form is invalid
        else:
            form=filled_form
            context={
                'form':form
                }
            return render(request,'base/login_register.html',context)

def verify_email_address(request, uidb64, token):
    user = get_user_from_email_verification_token(uidb64, token)
    if user != None:
        user.is_active = True
        user.save()
        login(request, user)
        
    return redirect('home')

def log_in(request):
    page = 'login'
    if request.method=="GET":
        #if request is GET check if user is already logged in
        if request.user.is_authenticated:
            #if logged in redirect
            return redirect('home')
        else:
            #if not logged in return login form
            form=LogInForm()
            context ={
                'form':form, 
                'page':page
                }
            return render(request,'base/login_register.html',context)

    
    elif request.method =="POST":
        #if request is a POST log in user
        page = 'login'
        filled_form = LogInForm(request.POST)
        if filled_form.is_valid():

            username=filled_form.cleaned_data.get('username_or_email')
            print(username)
            password=filled_form.cleaned_data.get('password')
            print(password)
            
            #check if username and password are correct
            user = authenticate(request, username=username, password=password)
            if user != None:
                #if a user is returned authentication was successful
                #log in the user

                login(request, user)
                try:
                    next = request.GET.get('next')
                except:
                    next = None
                if next is None:
                    return redirect('home')
                else:
                    return redirect(next)
            else:
                #if no user is returned authentication failed
                #add error
                filled_form.add_error(field=None,error='Incorrect username/email or password!')
                form=filled_form
                context = { 'form':form, 'page':page}
                return render(request,'base/login_register.html',{'form':form})
        else:
            form=filled_form
            return render(request,'base/login_register.html',{'form':form})

# def loginPage(request):
#     page = 'login'
#     if request.user.is_authenticated:
#         return redirect('home')
    
#     if request.method == 'POST':
#         email = request.POST.get('email').lower()
#         password = request.POST.get('password')

#         try:
#             user = User.objects.get(email=email)
#             print(user)
#         except:
#             messages.error(request, 'User not available!')

#         user = authenticate(request, email=email, password=password)
#         # print(user)

#         if user is not None:   
#             login(request,user)
#             return redirect('home')
#         else:
#             messages.error(request, 'Username or Password does not exist!')

#     context = {'page':page}
#     return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


# def registerUser(request):
#     form = MyuserCreationForm()

#     if request.method == 'POST':
#         form = MyuserCreationForm(request.POST)    
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password1 = form.cleaned_data.get('password1')
#             password2 = form.cleaned_data.get('password2')
#             if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password1):
#                 messages.error(request, 'Password must contain both letters and numbers, and be at least 8 characters long')
#                 return redirect('register')
#             if password1 != password2:
#                 messages.error(request, 'Passwords do not match')
#             user = form.save(commit=False)
#             user.username = user.username.lower()  
#             user.save()
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, 'An error occured during registration!')
            
    
#     context = {'form':form}
#     return render(request, 'base/login_register.html', context)


# def verify_email_address(request, uidb64, token):
#     user = get_user_from_email_verification_token(uidb64, token)
#     if user != None:
#         user.is_active = True
#         user.save()
#         login(request, user)
        
#     return redirect('loginPage')



@login_required(login_url='base/login/')
def password_change(request):
    current_user = User.objects.get(username=request.user.username)

    if request.method=="POST":
        filled_form=PasswordChangeForm(current_user,request.POST)

        if filled_form.is_valid():
            filled_form.save()
            return redirect('home')
        else:
            context = {'form':filled_form}
            return render(request,'base/changepassword.html',context)
        
    else:
        form=PasswordChangeForm(user=current_user)
        context = {'form':form}
        return render(request,'base/changepassword.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q)

    )

    room_messasges = Message.objects.filter(Q(room__topic__name__icontains=q))
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    context = {'rooms':rooms, 'topics': topics, 'room_count':room_count, 'room_messasges':room_messasges}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messasges = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':

        message  = Message.objects.create(
            # gets the logged in user
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        # adding the participant to many to many field
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messasges':room_messasges, 'participants':participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    # getting all the child components of room model
    rooms = user.room_set.all()
    room_messasges = user.message_set.all()
    topics  = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messasges':room_messasges, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('desccription')
        )
        return redirect('home')

    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='home')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form':form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics}

    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messasges = Message.objects.all()
    context = {'room_messasges':room_messasges}
    return render(request, 'base/activity.html', context)