from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_atividades, name='pagina_atividades'),
    path('editar/<int:id>/', views.editar_atividade, name='editar_atividade'),
    path('ativos/', views.atividades_ativas, name='atividades_ativas'),
    path('atividades/inativar/<int:id>/', views.inativar_atividade, name='inativar_atividade'),
    path('atividades/reativar/<int:id>/', views.reativar_atividade, name='reativar_atividade'),
]