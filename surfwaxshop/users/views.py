from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def login_user(request):
    return HttpResponse("login")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))
