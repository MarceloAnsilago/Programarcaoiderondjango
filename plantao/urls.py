from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_plantao, name='pagina_plantao'),
    path('salvar/', views.salvar_plantao, name='salvar_plantao'),
    path('listar/', views.listar_plantoes, name='listar_plantoes'),
    path('detalhar/<int:id>/', views.detalhar_plantao, name='detalhar_plantao'),
    path('editar/<int:id>/', views.editar_plantao, name='editar_plantao'),
    path('excluir/<int:id>/', views.excluir_plantao, name='excluir_plantao'),
    path('imprimir/<int:id>/', views.imprimir_plantao, name='imprimir_plantao'),
]