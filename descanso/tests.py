from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from datetime import date
from descanso.models import Descanso
from servidores.models import Servidor

class DescansoFiltroIntervaloTest(TestCase):
    def setUp(self):
        # Cria alguns servidores
        self.s1 = Servidor.objects.create(nome='Marcelo')
        self.s2 = Servidor.objects.create(nome='Letica')
        self.s3 = Servidor.objects.create(nome='Renato')

        # Cria descansos com vários intervalos
        Descanso.objects.create(servidor=self.s1, tipo_descanso='Férias', data_inicio=date(2025,7,1), data_fim=date(2025,7,24))
        Descanso.objects.create(servidor=self.s2, tipo_descanso='Licença', data_inicio=date(2025,7,2), data_fim=date(2025,7,31))
        Descanso.objects.create(servidor=self.s3, tipo_descanso='Férias', data_inicio=date(2025,6,28), data_fim=date(2025,7,5))  # começa antes, termina no período

    def test_filtro_intervalo(self):
        # Filtra no intervalo de 1 a 31 de julho
        dt_ini = date(2025, 7, 1)
        dt_fim = date(2025, 7, 31)

        descansos = Descanso.objects.filter(
            data_inicio__lte=dt_fim,
            data_fim__gte=dt_ini
        )

        nomes = set(d.servidor.nome for d in descansos)
        self.assertIn('Marcelo', nomes)
        self.assertIn('Letica', nomes)
        self.assertIn('Renato', nomes)
        self.assertEqual(len(nomes), 3)  # deve ter exatamente 3

    def test_filtro_sem_resultado(self):
        # Intervalo sem descanso
        dt_ini = date(2025, 8, 1)
        dt_fim = date(2025, 8, 31)
        descansos = Descanso.objects.filter(
            data_inicio__lte=dt_fim,
            data_fim__gte=dt_ini
        )
        self.assertEqual(descansos.count(), 0)
