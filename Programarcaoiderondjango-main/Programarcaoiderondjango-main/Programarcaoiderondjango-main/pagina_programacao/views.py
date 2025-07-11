from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Programacao, Alocacao
from atividades.models import Atividade
from servidores.models import Servidor
from veiculos.models import Veiculo

def pagina_programacao(request):
    return render(request, 'pagina_programacao.html')

@csrf_exempt
def salvar_programacao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(request.body)
            print("Recebido:", data)  # <-- veja no console
            print(data)  
            data_selecionada = data['data']
            programacoes = data['programacoes']

            Programacao.objects.filter(data=data_selecionada).delete()

            for card in programacoes:
                if not card['atividade_id']:
                    continue  # pula cards sem atividade
                atividade = Atividade.objects.get(pk=card['atividade_id'])
                veiculo = Veiculo.objects.get(pk=card['veiculo_id']) if card['veiculo_id'] else None
                prog = Programacao.objects.create(
                    atividade=atividade,
                    data=data_selecionada,
                    veiculo=veiculo,
                )
                for servidor_id in card['servidores']:
                    servidor = Servidor.objects.get(pk=servidor_id)
                    Alocacao.objects.create(programacao=prog, servidor=servidor)

            return JsonResponse({'ok': True})
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'ok': False, 'erro': str(e)})
    return JsonResponse({'ok': False, 'erro': 'Método não permitido'})
