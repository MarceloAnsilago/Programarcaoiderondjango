from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from supabase import create_client


def pagina_programacao(request):
    return render(request, 'pagina_programacao.html')

SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@csrf_exempt
def salvar_programacao(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            data = body.get('data')
            unidade_id = body.get('unidade_id', 1)
            alocacoes = body.get('alocacoes', [])

            # Cria UM registro de programacao para cada atividade+veiculo+data+unidade
            programacoes_ids = {}
            for aloc in alocacoes:
                atividade_id = aloc.get("atividade_id")
                veiculo_id = aloc.get("veiculo_id")
                chave = (atividade_id, data, unidade_id, veiculo_id)
                if chave not in programacoes_ids:
                    resp = supabase.table("programacoes").insert({
                        "atividade_id": atividade_id,
                        "data": data,
                        "unidade_id": unidade_id,
                        "veiculo_id": veiculo_id
                    }).execute()
                    prog_id = resp.data[0]['id']
                    programacoes_ids[chave] = prog_id

            # Agora, salve as alocações, ligando pelo programacao_id correto
            registros = []
            for aloc in alocacoes:
                atividade_id = aloc.get("atividade_id")
                veiculo_id = aloc.get("veiculo_id")
                chave = (atividade_id, data, unidade_id, veiculo_id)
                registros.append({
                    "programacao_id": programacoes_ids[chave],
                    "servidor_id": aloc.get("servidor_id"),
                    "atividade_id": atividade_id,
                    "data": data,
                    "unidade_id": unidade_id,
                    "veiculo_id": veiculo_id,
                })
            if registros:
                supabase.table("alocacoes").insert(registros).execute()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'msg': str(e)}, status=400)
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def datas_programadas(request):
    unidade_id = request.GET.get("unidade_id", 1)
    # Busca só datas distintas
    rows = supabase.table("programacoes") \
        .select("data") \
        .eq("unidade_id", int(unidade_id)) \
        .execute().data

    # Só datas únicas, formato 'YYYY-MM-DD'
    datas = list({row['data'] for row in rows if row.get('data')})
    return JsonResponse(datas, safe=False)



def detalhe_programacao(request):
    import json
    if request.method == "GET":
        data = request.GET.get('data')
        unidade_id = request.GET.get('unidade_id', 1)
        
        # Busca alocações daquele dia, naquela unidade
        alocacoes = (
            supabase.table("alocacoes")
            .select("atividade_id, servidor_id, veiculo_id, data, unidade_id, servidor:servidor_id(nome), atividade:atividade_id(nome), veiculo:veiculo_id(placa,modelo)")
            .eq("data", data)
            .eq("unidade_id", unidade_id)
            .execute()
            .data
        )
        
        # Organiza por atividade/card
        cards = {}
        for aloc in alocacoes:
            aid = aloc["atividade_id"]
            v_id = aloc.get("veiculo_id")
            # Nome dos relacionamentos:
            atividade_nome = (aloc.get("atividade") or {}).get("nome", "Expediente Administrativo") if aid else "Expediente Administrativo"
            veiculo_nome = None
            if v_id and aloc.get("veiculo"):
                veiculo_nome = f"{aloc['veiculo']['placa']} - {aloc['veiculo']['modelo']}"

            card_key = f"{aid}_{v_id or ''}"
            if card_key not in cards:
                cards[card_key] = {
                    "atividade_id": aid,
                    "atividade_nome": atividade_nome,
                    "veiculo_id": v_id,
                    "veiculo_nome": veiculo_nome,
                    "servidores": [],
                }
            cards[card_key]["servidores"].append({
                "id": aloc["servidor_id"],
                "nome": (aloc.get("servidor") or {}).get("nome", "")
            })

        return JsonResponse({"alocacoes": list(cards.values())})
    return JsonResponse({"erro": "Método não permitido"}, status=405)
