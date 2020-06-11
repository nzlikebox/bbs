from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse

from user.models import User
from user.forms import RegisterForm
from user.helper import login_required
# Create your views here.


def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)
            user.save()

            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            # return redirect('/user/info/')
            return HttpResponse('注册成功')
        else:
            return render(request, 'user_register.html', {'error': form.errors})
    return render(request, 'user_register.html')


def user_login(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return render(request, 'user_login.html', {'error': '用户名不存在'})
        if check_password(password, user.password):
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
        else:
            return render(request, 'user_login.html', {'error': '密码错误，请重新输入'})
    return render(request, 'user_login.html')


def user_logout(request):
    request.session.flush()
    return redirect('/user/login/')


@login_required
def user_info(request):
    uid = request.session.get('uid')
    user = User.objects.get(id=uid)
    return render(request, 'user_info.html', {'user': user})
