from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.apps import apps

User = apps.get_model('users', 'User')

def login_message_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "로그인한 사용자만 이용할 수 있습니다.")
            return redirect(settings.LOGIN_URL)

        return function(request, *args, **kwargs)

    return wrap

def my_decorator(view_func):
    def wrap(request, *args, **kwargs):
        # 어떤 로직 처리
        print("데코레이터에서 추가된 로직")
        response = view_func(request, *args, **kwargs)
        # 올바른 HttpResponse 객체 반환
        return response

    return wrap

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)

        messages.info(request, "접근 권한이 없습니다.")
        return redirect('/users/main/')

    return wrap


def logout_message_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "접속중인 사용자입니다.")
            return redirect('/users/main/')

        return function(request, *args, **kwargs)

    return wrap