import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from supabase import create_client
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from datetime import datetime
from datetime import datetime, timedelta
# Configurações do Supabase
SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def pagina_plantao(request):
    return render(request, 'plantao.html')

# --- Função utilitária para nomear semanas ---
def nomear_semana(data_str):
    try:
        # Converter a data fornecida
        data = datetime.strptime(data_str, "%Y-%m-%d").date()

        # Primeiro dia do mês
        primeiro_dia_mes = data.replace(day=1)

        # Retroagir até o domingo anterior ou o próprio domingo
        primeiro_dia_semana = primeiro_dia_mes - timedelta(days=primeiro_dia_mes.weekday() + 1) \
            if primeiro_dia_mes.weekday() != 6 else primeiro_dia_mes

        # Calcular diferença em dias entre a data e o primeiro domingo
        dias_passados = (data - primeiro_dia_semana).days

        # Calcular índice da semana visual
        semana_idx = dias_passados // 7

        nomes = [
            "Primeira semana", "Segunda semana", "Terceira semana",
            "Quarta semana", "Quinta semana", "Sexta semana"
        ]
        return nomes[semana_idx] if semana_idx < len(nomes) else f"{semana_idx + 1}ª semana"

    except Exception as e:
        print("[ERRO AO NOMEAR SEMANA]", str(e))
        return "Semana indefinida"

# --- View salvar_plantao ---
@csrf_exempt
def salvar_plantao(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=405)

    try:
        data = json.loads(request.body)
        nome = data.get('nome')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        escala = data.get('escala', [])
        unidade_id = 1

        if not (nome and data_inicio and data_fim and escala):
            return JsonResponse({'success': False, 'error': 'Dados incompletos'}, status=400)

        # Buscar plantões existentes para verificar conflitos
        conflitos_resp = supabase.table("plantoes") \
            .select("id, nome, data_inicio, data_fim") \
            .execute()

        conflitos_validos = []
        novo_ini = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        novo_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

        for p in conflitos_resp.data:
            ini = datetime.strptime(p["data_inicio"], "%Y-%m-%d").date()
            fim = datetime.strptime(p["data_fim"], "%Y-%m-%d").date()

            if not (novo_fim < ini or novo_ini > fim):
                conflitos_validos.append(p)

        if conflitos_validos:
            nomes_conflitantes = ", ".join([p['nome'] for p in conflitos_validos])
            return JsonResponse({
                'success': False,
                'error': f"Período informado conflita com os plantões: {nomes_conflitantes}"
            }, status=400)

        # Inserir novo plantão
        response = supabase.table("plantoes").insert([{
            "nome": nome,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "unidade_id": unidade_id
        }]).execute()

        if not response.data:
            raise Exception("Falha ao inserir plantão.")

        plantao_id = response.data[0]['id']

        # Inserir escala
        for item in escala:
            servidor_id = item.get('servidor_id')
            semana_inicio = item.get('semana_inicio')
            semana_fim = item.get('semana_fim')

            if not servidor_id or not semana_inicio or not semana_fim:
                continue

            nome_da_semana = nomear_semana(semana_inicio)

            escala_result = supabase.table("escala_plantao").insert([{
                "plantao_id": plantao_id,
                "servidor_id": servidor_id,
                "semana_inicio": semana_inicio,
                "semana_fim": semana_fim,
                "nome_da_semana": nome_da_semana
            }]).execute()

            if not escala_result.data:
                raise Exception("Erro ao salvar uma semana da escala.")

        return JsonResponse({'success': True, 'plantao_id': plantao_id})

    except Exception as e:
        print("[ERRO AO SALVAR PLANTÃO]", str(e))
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        })
@require_GET
def listar_plantoes(request):
    try:
        response = supabase.table("plantoes").select("*").order("data_inicio", desc=False).execute()
        data = response.data if hasattr(response, 'data') else []
        return JsonResponse({'success': True, 'plantoes': data})
    except Exception as e:
        import traceback
        print("[ERRO AO BUSCAR PLANTÕES]", str(e))
        return JsonResponse({'success': False, 'error': str(e), 'trace': traceback.format_exc()})    
    
@require_GET
def detalhar_plantao(request, id):
    resp_p = supabase.table('plantoes').select('*').eq('id', id).single().execute()
    plantao = resp_p.data

    resp_e = supabase.table('escala_plantao').select('*').eq('plantao_id', id).order('semana_inicio').execute()
    escala = resp_e.data

    # Agora também pegando telefone!
    resp_s = supabase.table('servidores').select('id, nome, telefone').execute()
    servidores = resp_s.data

    return JsonResponse({
        'plantao': plantao,
        'escala': escala,
        'servidoresDisponiveis': servidores
    })


@csrf_exempt
@require_http_methods(['PATCH'])
def editar_plantao(request, id):
    # Atualiza nome
    data = json.loads(request.body)
    supabase.table('plantoes').update({'nome': data['nome']}).eq('id', id).execute()
    # Recria escala
    supabase.table('escala_plantao').delete().eq('plantao_id', id).execute()
    for item in data['escala']:
        supabase.table('escala_plantao').insert([{
            'plantao_id': id,
            'servidor_id': item['servidor_id'],
            'semana_inicio': item['semana_inicio'],
            'semana_fim': item['semana_fim']
        }]).execute()
    return JsonResponse({'success': True})

@require_GET
def imprimir_plantao(request, id):
    # busca dados do Supabase
    resp_p = supabase.table('plantoes').select('*').eq('id', id).single().execute()
    plantao = resp_p.data
    resp_e = supabase.table('escala_plantao').select('*').eq('plantao_id', id).order('semana_inicio').execute()
    escala = resp_e.data

    return render(request, 'plantao_imprimir.html', {
        'plantao': plantao,
        'escala': escala
    })

@csrf_exempt
@require_http_methods(['DELETE'])
def excluir_plantao(request, id):
    supabase.table('escala_plantao').delete().eq('plantao_id', id).execute()
    supabase.table('plantoes').delete().eq('id', id).execute()
    return JsonResponse({'success': True})   


@require_GET
def descansos_intervalo(request):
    data_ini = request.GET.get("data_inicial")
    data_fim = request.GET.get("data_final")

    if not data_ini or not data_fim:
        return JsonResponse({"error": "Parâmetros obrigatórios"}, status=400)

    try:
        response = supabase.table("descansos") \
            .select("*") \
            .or_(f"data_inicio.lte.{data_fim},data_fim.gte.{data_ini}") \
            .execute()

        return JsonResponse(response.data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@require_GET


@require_GET
def listar_plantoes(request):
    try:
        response = supabase.table("plantoes").select("*").order("data_inicio", desc=False).execute()
        data = response.data if hasattr(response, 'data') else []

        # 🔍 Extrair apenas o ano do campo ISO `criado_em`
        anos = sorted({
            str(datetime.fromisoformat(p['criado_em']).year)
            for p in data if 'criado_em' in p and p['criado_em']
        })

        return JsonResponse({'success': True, 'plantoes': data, 'anos': anos})
    except Exception as e:
        import traceback
        print("[ERRO AO BUSCAR PLANTÕES]", str(e))
        return JsonResponse({'success': False, 'error': str(e), 'trace': traceback.format_exc()})


    
    