from django.db import models

# Create your models here.
class Atividade(models.Model):
    nome = models.CharField(max_length=100)
    status = models.TextField() 
    # adicione outros campos se necessário

    def __str__(self):
        return self.nome