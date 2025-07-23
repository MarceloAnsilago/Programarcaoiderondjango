# Create your models here.
from django.db import models

class Plantao(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    unidade_id = models.IntegerField()  # Pode virar ForeignKey se quiser

    class Meta:
        db_table = 'plantoes'  # Tabela real do banco
        managed = False        # Impede o Django de tentar criá-la


class EscalaPlantao(models.Model):
    plantao = models.ForeignKey(Plantao, on_delete=models.CASCADE)
    servidor_id = models.IntegerField()
    semana_inicio = models.DateField()
    semana_fim = models.DateField()

    class Meta:
        db_table = 'escala_plantao'
        managed = False