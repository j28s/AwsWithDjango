from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [

    path('main/', views.main_view, name='main'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('agreement/', views.AgreementView.as_view(), name='agreement'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('registerauth/', views.register_success, name='register_success'),
    path('activate/<str:uid64>/<str:token>/', views.activate, name='activate'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/post', views.profile_post_view, name='profile_post'),
    path('profile/comment', views.profile_comment_view, name='profile_comment'),
    path('profile/update/', views.profile_update_view, name='profile_update'),

]
