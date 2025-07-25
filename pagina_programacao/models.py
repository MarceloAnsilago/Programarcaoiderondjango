from django.db import models

class Programacoes(models.Model):
    data = models.DateField()
    unidade_id = models.IntegerField()
    atividade_id = models.IntegerField()
    veiculo_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'programacoes'  # 👈 forçando usar a tabela existente no Supabase
