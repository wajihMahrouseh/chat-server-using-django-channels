from django.shortcuts import render


def index(request):
    return render(request, "chatServerApp/index.html")


def room(request, room_name):
    return render(request, "chatServerApp/room.html", {"room_name": room_name})
