from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from supabase import create_client
from datetime import date, timedelta
from collections import defaultdict

SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def pagina_programacao(request):
    return render(request, 'pagina_programacao.html')


@csrf_exempt
def salvar_programacao(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            data = body.get('data')
            unidade_id = body.get('unidade_id', 1)
            alocacoes = body.get('alocacoes', [])

            # Remove todas as alocações/programações existentes daquele dia/unidade
            supabase.table("alocacoes").delete().eq("data", data).eq("unidade_id", unidade_id).execute()
            supabase.table("programacoes").delete().eq("data", data).eq("unidade_id", unidade_id).execute()

            # Insere as novas programações e alocações
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
    rows = supabase.table("programacoes").select("data").eq("unidade_id", int(unidade_id)).execute().data
    datas = list({row['data'] for row in rows if row.get('data')})
    return JsonResponse(datas, safe=False)

@csrf_exempt
def detalhe_programacao(request):
    if request.method == "GET":
        data = request.GET.get('data')
        unidade_id = request.GET.get('unidade_id', 1)
        alocacoes = (
            supabase.table("alocacoes")
            .select("atividade_id, servidor_id, veiculo_id, data, unidade_id, servidor:servidor_id(nome), atividade:atividade_id(nome), veiculo:veiculo_id(placa,modelo)")
            .eq("data", data)
            .eq("unidade_id", unidade_id)
            .execute()
            .data
        )
        cards = {}
        for aloc in alocacoes:
            aid = aloc["atividade_id"]
            v_id = aloc.get("veiculo_id")
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

        # >>>>>> ADICIONA O EXPEDIENTE SE NÃO EXISTE <<<<<<
        expediente = (
            supabase.table("atividades")
            .select("id")
            .eq("nome", "Expediente Administrativo")
            .eq("unidade_id", unidade_id)
            .single()
            .execute()
        )
        expediente_id = expediente.data["id"] if expediente and expediente.data else None

        ja_tem_expediente = any(
            str(card.get("atividade_id")) == str(expediente_id) for card in cards.values()
        )
        if expediente_id and not ja_tem_expediente:
            cards[f"{expediente_id}_"] = {
                "atividade_id": expediente_id,
                "atividade_nome": "Expediente Administrativo",
                "veiculo_id": None,
                "veiculo_nome": None,
                "servidores": [],
            }
        return JsonResponse({"alocacoes": list(cards.values())})
    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def resumo_alocacoes(request):
    unidade_id = int(request.GET.get('unidade_id', 1))
    data_str = request.GET.get('data')
    data_base = datetime.strptime(data_str, '%Y-%m-%d')
    semana_inicio = data_base - timedelta(days=data_base.weekday())
    semana_fim = semana_inicio + timedelta(days=6)
    mes_inicio = data_base.replace(day=1)
    if data_base.month == 12:
        mes_fim = data_base.replace(year=data_base.year+1, month=1, day=1) - timedelta(days=1)
    else:
        mes_fim = data_base.replace(month=data_base.month+1, day=1) - timedelta(days=1)

    def get_alocacoes(inicio, fim):
        return supabase.table("alocacoes") \
            .select("atividade_id, servidor_id, data, atividade:atividade_id(nome), servidor:servidor_id(nome)") \
            .eq("unidade_id", unidade_id) \
            .gte("data", inicio.strftime("%Y-%m-%d")) \
            .lte("data", fim.strftime("%Y-%m-%d")) \
            .execute().data

    def contar(alocacoes):
        resumo = {}
        for aloc in alocacoes:
            atividade_nome = (aloc.get("atividade") or {}).get("nome", "")
            if atividade_nome.strip().lower() == "expediente administrativo":
                continue
            servidor_nome = (aloc.get("servidor") or {}).get("nome", "")
            if not servidor_nome:
                continue
            resumo[servidor_nome] = resumo.get(servidor_nome, 0) + 1
        # Transforma em lista [{servidor: ..., quantidade: ...}]
        return [{"servidor": k, "quantidade": v} for k, v in resumo.items()]

    semana = contar(get_alocacoes(semana_inicio, semana_fim))
    mes = contar(get_alocacoes(mes_inicio, mes_fim))
  
    return JsonResponse({
        "semana": semana,
        "mes": mes
    })

def get_semanas_do_mes(ano, mes):
    semanas = []
    d = date(ano, mes, 1)
    while d.month == mes:
        inicio = d
        fim = inicio + timedelta(days=6 - inicio.weekday())
        if fim.month != mes:
            fim = date(ano, mes + 1, 1) - timedelta(days=1)
        semanas.append((inicio, fim))
        d = fim + timedelta(days=1)
    return semanas

def pagina_programacao(request):
    # Pega mês e ano do GET ou usa atual
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))
    semanas = list(enumerate(get_semanas_do_mes(ano, mes)))
    context = {
        'semanas': semanas,
        'semana_idx': 0, # ou pode receber via GET
    }
    return render(request, 'pagina_programacao.html', context)

from collections import defaultdict

from collections import defaultdict

@csrf_exempt
def api_programacao_semana(request):
    if request.method == "GET":
        unidade_id = int(request.GET.get('unidade_id', 1))
        semana_idx = int(request.GET.get('semana', 0))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))

        semanas = get_semanas_do_mes(ano, mes)
        if not semanas or semana_idx >= len(semanas):
            return JsonResponse({"erro": "Semana inválida"}, status=400)
        semana_inicio, semana_fim = semanas[semana_idx]

        # 1. Busca programações
        programacoes = supabase.table("programacoes")\
            .select("*, atividade:atividade_id(nome), veiculo:veiculo_id(placa,modelo)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", semana_inicio.isoformat())\
            .lte("data", semana_fim.isoformat())\
            .execute().data

        # 2. Busca alocações da semana (com servidores)
        alocacoes = supabase.table("alocacoes")\
            .select("programacao_id, servidor:servidor_id(nome)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", semana_inicio.isoformat())\
            .lte("data", semana_fim.isoformat())\
            .execute().data

        # 3. Indexa servidores por programação
        servidores_por_programacao = defaultdict(list)
        for aloc in alocacoes:
            if aloc.get("programacao_id") and aloc.get("servidor", {}).get("nome"):
                servidores_por_programacao[aloc["programacao_id"]].append(aloc["servidor"]["nome"])

        # 4. AGRUPA POR DATA e monta output
        result = defaultdict(list)
        for p in programacoes:
            data_str = p["data"]
            prog_id = p["id"]
            atividade_nome = p.get("atividade", {}).get("nome", p.get("atividade_id", ""))
            veiculo_nome = ""
            if p.get("veiculo"):
                veiculo_nome = f"{p['veiculo'].get('placa','')}"
                if p['veiculo'].get('modelo'):
                    veiculo_nome += " - " + p['veiculo']['modelo']
            result[data_str].append({
                "atividade": atividade_nome,
                "servidores": servidores_por_programacao.get(prog_id, []),
                "veiculo": veiculo_nome,
                "descricao": p.get("descricao", "")
            })
        return JsonResponse({"programacoes": result})

@csrf_exempt
def api_relatorio_semanal(request):
    if request.method == "GET":
        unidade_id = int(request.GET.get('unidade_id', 1))
        semana_idx = int(request.GET.get('semana', 0))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))

        semanas = get_semanas_do_mes(ano, mes)
        if not semanas or semana_idx >= len(semanas):
            return JsonResponse({"erro": "Semana inválida"}, status=400)
        semana_inicio, semana_fim = semanas[semana_idx]

        # Busca as alocações da semana, exceto Expediente Administrativo
        alocacoes = supabase.table("alocacoes") \
            .select("data, atividade:atividade_id(nome), servidor:servidor_id(nome)") \
            .eq("unidade_id", unidade_id) \
            .gte("data", semana_inicio.isoformat()) \
            .lte("data", semana_fim.isoformat()) \
            .execute().data

        servidores = defaultdict(list)
        for aloc in alocacoes:
            atividade_nome = (aloc.get("atividade") or {}).get("nome", "")
            if atividade_nome.lower().strip() == "expediente administrativo":
                continue
            servidor_nome = (aloc.get("servidor") or {}).get("nome", "")
            if not servidor_nome:
                continue
            servidores[servidor_nome].append({
                "data": aloc.get("data"),
                "atividade": atividade_nome,
            })

        return JsonResponse({"servidores": servidores})

@csrf_exempt
def api_programacao_mes(request):
    if request.method == "GET":
        unidade_id = int(request.GET.get('unidade_id', 1))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))

        # Pega o primeiro e último dia do mês
        from calendar import monthrange
        dia_inicio = date(ano, mes, 1)
        dia_fim = date(ano, mes, monthrange(ano, mes)[1])

        # 1. Busca programações do mês inteiro
        programacoes = supabase.table("programacoes")\
            .select("*, atividade:atividade_id(nome), veiculo:veiculo_id(placa,modelo)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", dia_inicio.isoformat())\
            .lte("data", dia_fim.isoformat())\
            .execute().data

        # 2. Busca alocações do mês inteiro
        alocacoes = supabase.table("alocacoes")\
            .select("programacao_id, servidor:servidor_id(nome)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", dia_inicio.isoformat())\
            .lte("data", dia_fim.isoformat())\
            .execute().data

        # 3. Indexa servidores por programação
        servidores_por_programacao = defaultdict(list)
        for aloc in alocacoes:
            if aloc.get("programacao_id") and aloc.get("servidor", {}).get("nome"):
                servidores_por_programacao[aloc["programacao_id"]].append(aloc["servidor"]["nome"])

        # 4. AGRUPA POR DATA e monta output
        result = defaultdict(list)
        for p in programacoes:
            data_str = p["data"]
            prog_id = p["id"]
            atividade_nome = p.get("atividade", {}).get("nome", p.get("atividade_id", ""))
            veiculo_nome = ""
            if p.get("veiculo"):
                veiculo_nome = f"{p['veiculo'].get('placa','')}"
                if p['veiculo'].get('modelo'):
                    veiculo_nome += " - " + p['veiculo']['modelo']
            result[data_str].append({
                "atividade": atividade_nome,
                "servidores": servidores_por_programacao.get(prog_id, []),
                "veiculo": veiculo_nome,
                "descricao": p.get("descricao", "")
            })
        return JsonResponse({"programacoes": result})
    return JsonResponse({"erro": "Método não permitido"}, status=405)

def api_programacao_meses_disponiveis(request):
    unidade_id = int(request.GET.get('unidade_id', 1))
    # Busca todas datas de programações
    rows = supabase.table("programacoes").select("data").eq("unidade_id", unidade_id).execute().data

    meses = set()
    for row in rows:
        if 'data' in row and row['data']:
            # Data sempre YYYY-MM-DD
            partes = row['data'].split('-')
            if len(partes) == 3:
                ano = partes[0]
                mes = partes[1]
                meses.add(f"{ano}-{mes}")

    # Deixa ordenado (mais antigo para mais recente)
    meses_ord = sorted(list(meses))
    meses_labels = []
    MES_LABELS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    for m in meses_ord:
        ano, mes = m.split('-')
        label = f"{MES_LABELS[int(mes)-1]}/{ano}"
        meses_labels.append({"mes": m, "label": label})

    return JsonResponse(meses_labels, safe=False)
@csrf_exempt
def api_relatorio_mensal(request):
    if request.method == "GET":
        unidade_id = int(request.GET.get('unidade_id', 1))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))
        from calendar import monthrange
        dia_inicio = date(ano, mes, 1)
        dia_fim = date(ano, mes, monthrange(ano, mes)[1])

        # Busca as alocações do mês, exceto Expediente Administrativo
        alocacoes = supabase.table("alocacoes") \
            .select("data, atividade:atividade_id(nome), servidor:servidor_id(nome)") \
            .eq("unidade_id", unidade_id) \
            .gte("data", dia_inicio.isoformat()) \
            .lte("data", dia_fim.isoformat()) \
            .execute().data

        servidores = defaultdict(list)
        for aloc in alocacoes:
            atividade_nome = (aloc.get("atividade") or {}).get("nome", "")
            if atividade_nome.lower().strip() == "expediente administrativo":
                continue
            servidor_nome = (aloc.get("servidor") or {}).get("nome", "")
            if not servidor_nome:
                continue
            servidores[servidor_nome].append({
                "data": aloc.get("data"),
                "atividade": atividade_nome,
            })

        return JsonResponse({"servidores": servidores})

    return JsonResponse({"erro": "Método não permitido"}, status=405)

def relatorio_semanal(request):
    # Sua lógica aqui
   return render(request, 'relatorios.html')

def relatorio_mensal(request):
    # Sua lógica aqui
    return render(request, 'relatorio_mensal.html')

