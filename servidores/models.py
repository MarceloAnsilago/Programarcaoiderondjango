from django.db import models

class Servidor(models.Model):
    nome = models.CharField(max_length=150)

    def __str__(self):
        return self.nome