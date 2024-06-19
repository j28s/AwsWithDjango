from django.conf import settings
from django.apps import apps
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# from .decorators import login_message_required, admin_required, logout_message_required
# from .decorators import admin_required, logout_message_required
from .decorators import login_message_required, admin_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView, TemplateView
from django.views.generic import View
from .models import User

from .forms import RegisterForm, LoginForm, CustomUserChangeForm
from django.http import HttpResponse
import json
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from .helper import send_mail, email_auth_num
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, Http404
from django.forms.utils import ErrorList
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import PermissionDenied

from django.apps import apps

# from .views import RegisterView


from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login

# from .forms import CsRegisterForm


Notice = apps.get_model('notice', 'Notice')
Free = apps.get_model('free', 'Free')
Comment = apps.get_model('free', 'Comment')
Anonymous = apps.get_model('anonymous', 'Anonymous')
AnonymousComment = apps.get_model('anonymous', 'AnonymousComment')
Calender = apps.get_model('calender', 'Calender')






# def index(request):
    # return render(request, 'users/main.html')


# 메인화면(로그인 후)
# @login_message_required
def main_view(request):
    notice_list = Notice.objects.order_by('-id')[:5]
    # calender_property = [x.event_id for x in Calender.objects.all() if x.d_day == False]
    calender_property = Calender.objects.filter(all_day=True)
    calendar_list = Calender.objects.exclude(event_id__in=calender_property).order_by('start_date')[:5]

    # calendar_list = Calender.objects.exclude(event_id__in=calender_property).order_by('start_date')[:5]
    free_list = Free.objects.filter(category='정보').order_by('-id')[:5]
    anonymous_list = sorted(Anonymous.objects.all(), key=lambda t: t.like_count, reverse=True)[:5]

    context = {
        'notice_list': notice_list,
        'calendar_list': calendar_list,
        'free_list': free_list,
        'anonymous_list': anonymous_list,
    }
    return render(request, 'users/main.html', context)


# 로그인
# @method_decorator(logout_message_required, name='dispatch')
class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = '/users/main/'

    def form_valid(self, form):
        user_id = form.cleaned_data.get("user")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=user_id, password=password)
        if user is not None:
            self.request.session['user'] = user
            login(self.request, user)

            # Session Maintain Test

            remember_session = self.request.POST.get('remember_session', False)
            if remember_session:
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False

            try:
                remember_session = self.request.POST['remember_session']
                if remember_session:
                    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
            except MultiValueDictKeyError:
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

        return super().form_valid(form)


# 로그아웃
def logout_view(request):
    logout(request)
    return redirect('/')


# 회원가입 약관동의
# @method_decorator(logout_message_required, name='dispatch')
class AgreementView(View):
    def get(self, request, *args, **kwargs):
        request.session['agreement'] = False
        return render(request, 'users/agreement.html')

    def post(self, request, *args, **kwarg):
        if request.POST.get('agreement1', False) and request.POST.get('agreement2', False):
            request.session['agreement'] = True
            if request.POST.get('csregister') == 'csregister':
                return redirect('/users/csregister/')
            else:
                return redirect('/users/register/')
        else:
            messages.info(request, "약관에 모두 동의해주세요.")
            return render(request, 'users/agreement.html')


# 회원가입 인증메일 발송 안내 창
def register_success(request):
    if not request.session.get('register_auth', False):
        raise PermissionDenied
    request.session['register_auth'] = False

    return render(request, 'users/register_success.html')


# 회원가입
class RegisterView(CreateView):
    model = User
    template_name = 'users/register.html'
    form_class = RegisterForm

    def get(self, request, *args, **kwargs):
        if not request.session.get('agreement', False):
            raise PermissionDenied
        request.session['agreement'] = False

        url = settings.LOGIN_REDIRECT_URL
        if request.user.is_authenticated:
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        # messages.success(self.request, "회원가입 성공.")
        self.request.session['register_auth'] = True
        messages.success(self.request, '회원님의 입력한 Email 주소로 인증 메일이 발송되었습니다. 인증 후 로그인이 가능합니다.')
        return settings.LOGIN_URL
        # return reverse('users:register_success')

    def form_valid(self, form):
        self.object = form.save()

        send_mail(
            '[Pit A Pat] {}님의 회원가입 인증메일 입니다.'.format(self.object.user_id),
            [self.object.email],
            html=render_to_string('users/register_email.html', {
                'user': self.object,
                'uid': urlsafe_base64_encode(force_bytes(self.object.pk)).encode().decode(),
                'domain': self.request.META['HTTP_HOST'],
                'token': default_token_generator.make_token(self.object),
            }),
        )

        return redirect(self.get_success_url())


def activate(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        current_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        messages.error(request, '메일 인증에 실패했습니다.')
        return redirect('users:login')

    if default_token_generator.check_token(current_user, token):
        current_user.is_active = True
        current_user.save()

        messages.info(request, '메일 인증이 완료 되었습니다. 회원가입을 축하드립니다!')
        return redirect('users:login')

    messages.error(request, '메일 인증에 실패했습니다.')
    return redirect('users:login')


# 프로필 보기
# @login_message_required
def profile_view(request):
    if request.method == 'GET':
        return render(request, 'users/profile.html')


# 프로필 수정
# @login_message_required
def profile_update_view(request):
    if request.method == 'POST':

        user_change_form = CustomUserChangeForm(request.POST, instance=request.user)

        if user_change_form.is_valid():
            user_change_form.save()
            messages.success(request, '회원정보가 수정되었습니다.')
            return render(request, 'users/profile.html')
    else:

        user_change_form = CustomUserChangeForm(instance=request.user)

        return render(request, 'users/profile_update.html', {'user_change_form': user_change_form})




# 내가 쓴 글 보기
# @login_message_required
@require_GET
def profile_post_view(request):
    free_list = Free.objects.filter(writer=request.user.id).order_by('-registered_date')
    anonymous_list = Anonymous.objects.filter(writer=request.user.id).order_by('-registered_date')
    context = {
        'free_list': free_list,
        'anonymous_list': anonymous_list,
    }
    if request.user.is_superuser:
        notice_list = Notice.objects.filter(writer=request.user.id).order_by('-registered_date')
        context['notice_list'] = notice_list

    return render(request, 'users/profile_post.html', context)


# 댓글 단 글 보기
# @login_message_required
@require_GET
def profile_comment_view(request):
    comment_list = Comment.objects.select_related('post').filter(writer=request.user).exclude(deleted=True).order_by(
        '-created')
    anonymous_comment_list = AnonymousComment.objects.select_related('post').filter(writer=request.user).exclude(
        deleted=True).order_by('-created')
    context = {
        'comment_list': comment_list,
        'anonymous_comment_list': anonymous_comment_list,
    }
    return render(request, 'users/profile_comment.html', context)
