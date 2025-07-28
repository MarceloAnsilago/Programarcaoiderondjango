from django.urls import path
from . import views


urlpatterns = [
    path('', views.pagina_servidores, name='pagina_servidores'),
    path('editar/<int:servidor_id>/', views.editar_servidor, name='editar_servidor'),
    path('inativar/<int:servidor_id>/', views.inativar_servidor, name='inativar_servidor'),  # 🚨 NOVO: Inativar em vez de excluir
    path('ativos/', views.servidores_ativos, name='servidores_ativos'),
    path('reativar/<int:servidor_id>/', views.reativar_servidor, name='reativar_servidor'),

]