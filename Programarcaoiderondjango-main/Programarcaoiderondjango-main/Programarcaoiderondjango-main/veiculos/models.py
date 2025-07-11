from django.db import models

class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    cor = models.CharField(max_length=30, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.placa} - {self.modelo}"