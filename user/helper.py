import requests
from django.shortcuts import redirect


def login_required(view_func):
    def wrapper(request):
        if request.session.get('uid') is None:
            return redirect('/user/login/')
        else:
            return view_func(request)
    return wrapper

