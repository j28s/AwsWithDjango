from django import forms
from django.contrib.auth.hashers import check_password
from .models import User
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, SetPasswordForm, UserCreationForm, \
    PasswordChangeForm
from django.contrib.auth import get_user_model
from .choice import *


def hp_validator(value):
    if len(str(value)) < 0:
        raise forms.ValidationError('정확한 핸드폰 번호를 입력해주세요.')


def student_id_validator(value):
    if len(str(value)) != 9:
        raise forms.ValidationError('본인의 학번 9자리를 입력해주세요.')


# 로그인 폼
class LoginForm(forms.Form):
    user_id = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', }),
        error_messages={
            'required': '아이디을 입력해주세요.'
        },
        max_length=32,
        label='아이디'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', }),
        error_messages={
            'required': '비밀번호를 입력해주세요.'
        },
        label='비밀번호'
    )

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        password = cleaned_data.get('password')
        if user_id and password:
            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:  # 사용자가 없을 경우에도 일반적인 오류로 처리
                user = None

            if user is not None and not check_password(password, user.password):
                self.add_error('password', '비밀번호가 틀렸습니다.')
            elif user is None:
                self.add_error('user_id', '아이디가 존재하지 않습니다.')


# 일반회원정보 수정 폼
class CustomUserChangeForm(UserChangeForm):
    password = None

    hp = forms.IntegerField(label='연락처', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'maxlength': '11', 'oninput': "maxLengthCheck(this)", }),
                            )
    name = forms.CharField(label='이름', widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength': '8', }),
                           )
    student_id = forms.IntegerField(required=False, label='학번', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'maxlength': '8', 'oninput': "maxLengthCheck(this)", }),
                                    )
    grade = forms.ChoiceField(choices=GRADE_CHOICES, label='학년', widget=forms.Select(
        attrs={'class': 'form-control', }),
                              )
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, label='학과', widget=forms.Select(
        attrs={'class': 'form-control', }),
                                   )

    class Meta:
        model = get_user_model()
        fields = ['hp', 'name', 'student_id', 'grade', 'department']


# 일반 회원가입 폼
class RegisterForm(UserCreationForm):
    student_id = forms.IntegerField(validators=[student_id_validator], required=False, label='학번',
                                    widget=forms.NumberInput(
                                        attrs={'class': 'form-control', }),
                                    )
    grade = forms.ChoiceField(choices=GRADE_CHOICES, label='학년', widget=forms.Select(
        attrs={'class': 'form-control'}),
                              )
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, label='학과', widget=forms.Select(
        attrs={'class': 'form-control'}),
                                   )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['user_id'].label = '아이디'
        self.fields['user_id'].widget.attrs.update({
            # 'class': 'form-control col-sm-10',
            'class': 'form-control',
            'autofocus': False,
            # 'placeholder': '아이디를 입력해주세요.',
        })
        self.fields['password1'].label = '비밀번호'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '비밀번호를 입력해주세요.',
        })
        self.fields['password2'].label = '비밀번호 확인'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '비밀번호를 다시 입력해주세요.',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '회원가입 후 입력하신 메일로 본인인증 메일이 전송됩니다.',
        })
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "아이디, 비밀번호 찾기에 이용됩니다.",
        })
        self.fields['hp'].label = '핸드폰번호'
        self.fields['hp'].validators = [hp_validator]
        self.fields['hp'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })

    class Meta:
        model = User
        fields = ['user_id', 'password1', 'password2', 'email', 'name', 'hp', 'department', 'grade', 'student_id']
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        # user.level = '2'
        user.circles = 'Pit A Pat'
        user.is_active = False
        user.save()
        return user