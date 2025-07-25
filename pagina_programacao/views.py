from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from calendar import monthrange
from supabase import create_client
from datetime import date, timedelta
from collections import defaultdict
from .models import Programacoes 

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

        # CORRIGIDO: Usa último dia do mês
        ultimo_dia = monthrange(ano, mes)[1]
        if fim.month != mes:
            fim = date(ano, mes, ultimo_dia)

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


@csrf_exempt
def api_programacao_semana(request):
    if request.method == "GET":
        try:
            unidade_id = int(request.GET.get('unidade_id', 1))
            semana_idx = int(request.GET.get('semana', 0))
            ano = int(request.GET.get('ano', date.today().year))
            mes = int(request.GET.get('mes', date.today().month))

            semanas = get_semanas_do_mes(ano, mes)

            print(f"📅 Ano: {ano} | Mês: {mes} | Semana índice: {semana_idx}")
            print(f"🗓️ Semanas calculadas: {semanas}")

            if not semanas or semana_idx < 0 or semana_idx >= len(semanas):
                return JsonResponse({"erro": "Semana inválida selecionada."}, status=400)

            semana_inicio, semana_fim = semanas[semana_idx]

            # 1. Programações
            programacoes = supabase.table("programacoes")\
                .select("*, atividade:atividade_id(nome), veiculo:veiculo_id(placa,modelo)")\
                .eq("unidade_id", unidade_id)\
                .gte("data", semana_inicio.isoformat())\
                .lte("data", semana_fim.isoformat())\
                .execute().data

            # 2. Alocações
            alocacoes = supabase.table("alocacoes")\
                .select("programacao_id, servidor:servidor_id(nome)")\
                .eq("unidade_id", unidade_id)\
                .gte("data", semana_inicio.isoformat())\
                .lte("data", semana_fim.isoformat())\
                .execute().data

            # 3. Servidores indexados por programação
            servidores_por_programacao = defaultdict(list)
            for aloc in alocacoes:
                nome = aloc.get("servidor", {}).get("nome")
                if aloc.get("programacao_id") and nome:
                    servidores_por_programacao[aloc["programacao_id"]].append(nome)

            # 4. Organiza atividades por data
            result = defaultdict(list)
            for p in programacoes:
                data_str = p["data"]
                prog_id = p["id"]
                atividade_nome = p.get("atividade", {}).get("nome", p.get("atividade_id", ""))
                veiculo_nome = ""
                if p.get("veiculo"):
                    veiculo_nome = p["veiculo"].get("placa", "")
                    modelo = p["veiculo"].get("modelo")
                    if modelo:
                        veiculo_nome += f" - {modelo}"
                result[data_str].append({
                    "atividade": atividade_nome,
                    "servidores": servidores_por_programacao.get(prog_id, []),
                    "veiculo": veiculo_nome,
                    "descricao": p.get("descricao", "")
                })

            # 5. Buscar plantonista da semana
            plantonista_nome = None
            try:
                escalas = supabase.table("escala_plantao")\
                    .select("*, servidor:servidor_id(nome), plantao:plantao_id(unidade_id)")\
                    .or_(f"semana_inicio.lte.{semana_fim.isoformat()},semana_fim.gte.{semana_inicio.isoformat()}")\
                    .execute().data

                print(f"🔍 Escalas encontradas: {len(escalas)}")

                
                for escala in escalas:
                    plantao = escala.get("plantao")
                    if not plantao or plantao.get("unidade_id") != unidade_id:
                        continue

                    inicio = escala.get("semana_inicio")
                    fim = escala.get("semana_fim")

                    if inicio and fim:
                        # Verifica se há sobreposição entre as semanas
                        if not (semana_fim < date.fromisoformat(inicio) or semana_inicio > date.fromisoformat(fim)):
                            nome_servidor = escala.get("servidor", {}).get("nome")
                            if nome_servidor:
                                plantonista_nome = nome_servidor.strip().title()
                                break

            except Exception as e:
                print("⚠️ Erro ao buscar escalas:", str(e))

            return JsonResponse({
                "programacoes": result,
                "plantonista": plantonista_nome
            })

        except Exception as e:
            print("❌ Erro interno:", str(e))
            return JsonResponse({"erro": "Erro interno ao processar a semana"}, status=500)


            
@csrf_exempt
def api_relatorio_semanal(request):
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        unidade_id = int(request.GET.get('unidade_id', 1))
        semana_idx = int(request.GET.get('semana', 0))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))

        semanas = get_semanas_do_mes(ano, mes)
        if not semanas or semana_idx < 0 or semana_idx >= len(semanas):
            return JsonResponse({"erro": "Semana inválida"}, status=400)

        semana_inicio, semana_fim = semanas[semana_idx]

        # 🎯 Coleta as alocações da semana
        alocacoes = supabase.table("alocacoes")\
            .select("data, atividade:atividade_id(nome), servidor:servidor_id(nome)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", semana_inicio.isoformat())\
            .lte("data", semana_fim.isoformat())\
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

        # 🛡️ Busca do plantonista exato pela data da semana
        plantonista_nome = None
        try:
            escala = supabase.table("escala_plantao")\
                .select("*, servidor:servidor_id(nome), plantao:plantao_id(unidade_id)")\
                .eq("semana_inicio", semana_inicio.isoformat())\
                .eq("semana_fim", semana_fim.isoformat())\
                .execute().data

            for item in escala:
                if item.get("plantao", {}).get("unidade_id") == unidade_id:
                    nome = item.get("servidor", {}).get("nome")
                    if nome:
                        plantonista_nome = nome.strip().title()
                        break
        except Exception as e:
            print("⚠️ Erro ao buscar plantonista:", str(e))

        return JsonResponse({
            "servidores": servidores,
            "plantonista": plantonista_nome
        })

    except Exception as e:
        print("❌ Erro interno:", str(e))
        return JsonResponse({"erro": "Erro ao processar relatório semanal"}, status=500)
@csrf_exempt
def api_programacao_mes(request):
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        unidade_id = int(request.GET.get('unidade_id', 1))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))

        dia_inicio = date(ano, mes, 1)
        dia_fim = date(ano, mes, monthrange(ano, mes)[1])

        # 1. Programações
        programacoes = supabase.table("programacoes")\
            .select("*, atividade:atividade_id(nome), veiculo:veiculo_id(placa,modelo)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", dia_inicio.isoformat())\
            .lte("data", dia_fim.isoformat())\
            .execute().data

        # 2. Alocações
        alocacoes = supabase.table("alocacoes")\
            .select("programacao_id, servidor:servidor_id(nome)")\
            .eq("unidade_id", unidade_id)\
            .gte("data", dia_inicio.isoformat())\
            .lte("data", dia_fim.isoformat())\
            .execute().data

        # 3. Servidores por programação
        servidores_por_programacao = defaultdict(list)
        for aloc in alocacoes:
            nome = aloc.get("servidor", {}).get("nome")
            if aloc.get("programacao_id") and nome:
                servidores_por_programacao[aloc["programacao_id"]].append(nome)

        # 4. Agrupa por data
        result = defaultdict(list)
        for p in programacoes:
            data_str = p["data"]
            prog_id = p["id"]
            atividade_nome = p.get("atividade", {}).get("nome", p.get("atividade_id", ""))
            veiculo_nome = ""
            if p.get("veiculo"):
                veiculo_nome = p["veiculo"].get("placa", "")
                modelo = p["veiculo"].get("modelo")
                if modelo:
                    veiculo_nome += f" - {modelo}"
            result[data_str].append({
                "atividade": atividade_nome,
                "servidores": servidores_por_programacao.get(prog_id, []),
                "veiculo": veiculo_nome,
                "descricao": p.get("descricao", "")
            })

        return JsonResponse({"programacoes": result})

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
    

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
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        unidade_id = int(request.GET.get('unidade_id', 1))
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))

        dia_inicio = date(ano, mes, 1)
        dia_fim = date(ano, mes, monthrange(ano, mes)[1])

        # ⏱️ Semanas do mês
        semanas = get_semanas_do_mes(ano, mes)

        # 📊 Alocações do mês
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

        # 🔍 Buscar plantonistas por semana


        return JsonResponse({
            "servidores": servidores,
          
        })

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

def relatorio_semanal(request):
    # Sua lógica aqui
   return render(request, 'relatorios.html')

def relatorio_mensal(request):
    # Sua lógica aqui
    return render(request, 'relatorio_mensal.html')



@csrf_exempt
@csrf_exempt
def excluir_programacao(request):
    if request.method == 'POST':
        try:
            print("🔍 Requisição recebida (POST):", request.body)

            if not request.body:
                print("⚠️ Body vazio")
                return JsonResponse({'status': 'erro', 'msg': 'Body vazio'})

            body = json.loads(request.body)
            print("📦 JSON recebido:", body)

            if body.get('_method') != 'DELETE':
                print("⚠️ Método não é DELETE")
                return JsonResponse({'status': 'erro', 'msg': 'Método inválido'})

            data_str = body.get('data')
            unidade_id = int(body.get('unidade_id'))
            print("🗓️ Data:", data_str, "| 🏢 Unidade ID:", unidade_id)

            if not data_str or not unidade_id:
                print("⚠️ Parâmetros ausentes")
                return JsonResponse({'status': 'erro', 'msg': 'Parâmetros ausentes'})

            # Exclui alocações vinculadas à data + unidade
            aloc_res = supabase.table("alocacoes")\
                .delete()\
                .eq("data", data_str)\
                .eq("unidade_id", unidade_id)\
                .execute()

            # Exclui programações vinculadas à data + unidade
            prog_res = supabase.table("programacoes")\
                .delete()\
                .eq("data", data_str)\
                .eq("unidade_id", unidade_id)\
                .execute()

            total_excluidos = len((aloc_res.data or [])) + len((prog_res.data or []))
            print(f"🧹 Registros removidos: {total_excluidos}")

            if total_excluidos > 0:
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'erro', 'msg': 'Nada foi excluído'})

        except json.JSONDecodeError:
            print("❌ JSON malformado")
            return JsonResponse({'status': 'erro', 'msg': 'JSON inválido'})
        except Exception as e:
            print("❌ Erro inesperado:", e)
            return JsonResponse({'status': 'erro', 'msg': str(e)})

    print("⚠️ Método não permitido")
    return JsonResponse({'status': 'erro', 'msg': 'Método não permitido'})
