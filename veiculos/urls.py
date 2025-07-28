from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_veiculos, name='pagina_veiculos'),
    path('editar/<int:id>/', views.editar_veiculos, name='editar_veiculos'),
    path('inativar/<int:id>/', views.inativar_veiculo, name='inativar_veiculo'),
    path('reativar/<int:id>/', views.reativar_veiculo, name='reativar_veiculo'),
    path('ativos/', views.veiculos_ativos, name='veiculos_ativos'),
]