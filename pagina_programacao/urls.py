from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_programacao, name='pagina_programacao'),
    path('salvar_programacao/', views.salvar_programacao, name='salvar_programacao'),
    path('datas_programadas/', views.datas_programadas, name='datas_programadas'),
    path('detalhe/', views.detalhe_programacao, name='detalhe_programacao'),
    path('resumo_alocacoes/', views.resumo_alocacoes, name='resumo_alocacoes'),
    path('api/programacao-semana/', views.api_programacao_semana, name='api_programacao_semanal'),
    path('api/relatorio-semanal/', views.api_relatorio_semanal, name='api_relatorio_semanal'),   # <----- ESSA LINHA!!!
    path('relatorio/semanal/', views.relatorio_semanal, name='relatorio_semanal'),
    path('relatorio/mensal/', views.relatorio_mensal, name='relatorio_mensal'),
    path('api/programacao-mes/', views.api_programacao_mes, name='api_programacao_mes'),
    path('api/programacao-meses-disponiveis/', views.api_programacao_meses_disponiveis, name='programacao_meses_disponiveis'),
    path('api/relatorio-mensal/', views.api_relatorio_mensal, name='api_relatorio_mensal'),
]

