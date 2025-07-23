from django.urls import path
from descanso import views as descanso_views
from descanso.views import descansos_intervalo
urlpatterns = [
    path('', descanso_views.lista_servidores_ativos, name='lista_servidores_ativos'),
    path('<int:servidor_id>/adicionar/', descanso_views.adicionar_descanso, name='adicionar_descanso'),
    path('descanso/<int:descanso_id>/editar/', descanso_views.editar_descanso, name='editar_descanso'),
    path('descanso/<int:descanso_id>/excluir/', descanso_views.excluir_descanso, name='excluir_descanso'),
    path("api/descansos_na_data/", descanso_views.servidores_em_descanso_na_data, name="descansos_na_data"),

    # 👇 NOVOS ENDPOINTS PARA RELATÓRIOS
    path("api/descansos-semana/", descanso_views.descansos_na_semana, name="descansos_semana"),
    path("api/descansos-mes/", descanso_views.descansos_do_mes, name="descansos_mes"),
    path('api/descansos-intervalo/', descansos_intervalo, name='descansos_intervalo'),
]