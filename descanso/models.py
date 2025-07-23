from django.db import models
from servidores.models import Servidor
from django.db import models


class Descanso(models.Model):
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    tipo_descanso = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    def __str__(self):
        return f"{self.servidor} - {self.tipo_descanso} ({self.data_inicio} a {self.data_fim})"

