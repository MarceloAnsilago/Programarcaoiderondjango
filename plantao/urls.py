from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_plantao, name='pagina_plantao'),
]