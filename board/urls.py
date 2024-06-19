from django.urls import path
from . import views

app_name = 'board'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/vote/', views.vote, name='vote'),
    path('<int:pk>/results/', views.results, name='results'),
]
