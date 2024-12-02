from django.shortcuts import render
from django.http import HttpResponse



class DemoException(Exception):
    pass

def home(request,*args,**kargs):
    print("view")
    # raise DemoException("DemoException")
    if request.method == "GET":
        print(request.GET)
    return HttpResponse(
        """Hello, Django!
        <form methode='GET' action='/1'>
        <input type='text' name='name'>
        <input type='submit'>
        </form>
        """)