from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_atividades, name='pagina_atividades'),
    path('excluir/<int:id>/', views.excluir_atividade, name='excluir_atividade'),
    path('editar/<int:id>/', views.editar_atividade, name='editar_atividade'),
    path('ativos/', views.atividades_ativas, name='atividades_ativas'),
]