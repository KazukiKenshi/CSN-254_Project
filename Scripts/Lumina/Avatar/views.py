from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def test(request):

    context = {}
    
    return render(request,'Avatar/index.html',context)

