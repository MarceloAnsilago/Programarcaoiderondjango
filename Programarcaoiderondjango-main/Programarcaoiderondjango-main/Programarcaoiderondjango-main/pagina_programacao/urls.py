from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_programacao, name='pagina_programacao'),
    path('salvar_programacao/', views.salvar_programacao, name='salvar_programacao'),
    path('datas_programadas/', views.datas_programadas, name='datas_programadas'),
    path('detalhe/', views.detalhe_programacao, name='detalhe_programacao'),
    

]

