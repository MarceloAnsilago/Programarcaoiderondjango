from django.db import models

class Servidor(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome