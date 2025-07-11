from django.db import models
from atividades.models import Atividade
from servidores.models import Servidor
from veiculos.models import Veiculo

class Programacao(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    data = models.DateField()
    # unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)  # Removido temporariamente
    veiculo = models.ForeignKey(Veiculo, null=True, blank=True, on_delete=models.SET_NULL)

class Alocacao(models.Model):
    programacao = models.ForeignKey(Programacao, on_delete=models.CASCADE, related_name='alocacoes')
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)