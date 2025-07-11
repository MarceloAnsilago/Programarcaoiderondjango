from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_veiculos, name='pagina_veiculos'),
    path('editar/<int:id>/', views.editar_veiculos, name='editar_veiculos'),
    path('excluir/<int:id>/', views.excluir_veiculos, name='excluir_veiculos'),
    path('ativos/', views.veiculos_ativos, name='veiculos_ativos'),
]