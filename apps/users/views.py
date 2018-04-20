from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    '''进入首页'''

    return HttpResponse('首页')