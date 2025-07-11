from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_programacao, name='pagina_programacao'),
    path('api/salvar/', views.salvar_programacao, name='salvar_programacao'),
]