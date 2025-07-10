from django.urls import path
from . import views


urlpatterns = [
    path('', views.pagina_servidores, name='pagina_servidores'),
    path('excluir/<int:servidor_id>/', views.excluir_servidor, name='excluir_servidor'),
    path('editar/<int:servidor_id>/', views.editar_servidor, name='editar_servidor'),
    path('ativos/', views.servidores_ativos, name='servidores_ativos'),
]