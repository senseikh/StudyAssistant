from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message,User
from .forms import RoomForm,UserForm,MyuserCreationForm

# Create your views here.

# rooms = [
#   {"id": 1,"name": "Mustang learninh"},
#   {"id": 2,"name": "toyota learning"},
#   {"id": 3,"name": "benz learning"}
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            print(user)
        except:
            messages.error(request, 'User not available!')

        user = authenticate(request, email=email, password=password)
        # print(user)

        if user is not None:   
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist!')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = MyuserCreationForm()

    if request.method == 'POST':
        form = MyuserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration!')

    context = {'form':form}
    return render(request, 'base/login_register.html', context)



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