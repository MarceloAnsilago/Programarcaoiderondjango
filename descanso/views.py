from django.shortcuts import render, redirect
from supabase import create_client
from datetime import datetime, timedelta  
from django.http import JsonResponse
import calendar

SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def lista_servidores_ativos(request):
    try:
        unidade_id = 1  # depois altere para o usuário logado
        ano_selecionado = request.GET.get('ano')

        # Buscar datas de criação dos descansos
        resp = supabase.table("descansos").select("criado_em").execute()
        datas_criacao = resp.data or []

        # Ignora nulos e converte para ano
        anos_unicos = sorted({
            datetime.fromisoformat(d["criado_em"]).year
            for d in datas_criacao
            if d.get("criado_em")
        })

        # Buscar servidores ativos da unidade
        servidores = supabase.table("servidores") \
            .select("*") \
            .eq("status", "Ativo") \
            .eq("unidade_id", unidade_id) \
            .execute().data or []

        servidores_filtrados = []
        descansos_todos = []

        for s in servidores:
            query = supabase.table("descansos").select("*").eq("servidor_id", s["id"])
            if ano_selecionado:
                data_ini = f"{ano_selecionado}-01-01T00:00:00"
                data_fim = f"{ano_selecionado}-12-31T23:59:59"
                query = query.gte("criado_em", data_ini).lte("criado_em", data_fim)

            descansos_filtrados = query.execute().data or []

            if descansos_filtrados:
                s["descansos"] = descansos_filtrados
                servidores_filtrados.append(s)
                descansos_todos.extend(descansos_filtrados)

        ano_mapa = int(ano_selecionado) if ano_selecionado else datetime.now().year

        servidores_mapa = supabase.table("servidores").select("id, nome").execute().data or []
        meses = []

        for mes in range(1, 13):
            dias_do_mes = list(range(1, calendar.monthrange(ano_mapa, mes)[1] + 1))
            linhas_servidor = []
            for s in servidores_mapa:
                periodos = []
                for d in descansos_todos:
                    if d["servidor_id"] == s["id"]:
                        try:
                            data_ini = datetime.strptime(d["data_inicio"], "%Y-%m-%d").date()
                            data_fim = datetime.strptime(d["data_fim"], "%Y-%m-%d").date()
                            dias = [
                                dt.day for dt in (
                                    data_ini + timedelta(days=n)
                                    for n in range((data_fim - data_ini).days + 1)
                                ) if dt.year == ano_mapa and dt.month == mes
                            ]
                            periodos += dias
                        except Exception:
                            continue  # ignora erro de data malformada
                if periodos:
                    linhas_servidor.append({
                        "nome": s["nome"],
                        "periodos_dias": sorted(set(periodos))
                    })
            meses.append({
                "numero": mes,
                "nome": calendar.month_name[mes].capitalize(),
                "dias": dias_do_mes,
                "linhas_servidor": linhas_servidor
            })

        context = {
            "servidores": servidores_filtrados if ano_selecionado else servidores,
            "anos_unicos": anos_unicos,
            "ano_selecionado": ano_selecionado,
            "meses": meses,
            "ano": ano_mapa
        }
        return render(request, "descanso.html", context)

    except Exception as e:
        # Renderiza erro amigável na página
        return render(request, "erro_supabase.html", {
            "mensagem": f"Ocorreu um erro ao acessar os dados da Supabase: {e}"
        })

def lista_descansos_servidor(request, servidor_id):
    descansos = (
        supabase.table("descansos")
        .select("*")
        .eq("servidor_id", servidor_id)
        .execute()
        .data
    )
    return render(request, "descanso_servidor.html", {
        "descansos": descansos,
        "servidor_id": servidor_id
    })

def adicionar_descanso(request, servidor_id):
    erro = ""
    tipos_descanso = [
        "Férias", "Folga Compensatória", "Atestado", "Afastamento", "Licença", "Outros"
    ]
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        data_inicio = request.POST.get("data_inicio")
        data_fim = request.POST.get("data_fim")
        observacao = request.POST.get("observacao")

        if data_inicio and data_fim and data_fim < data_inicio:
            erro = "A data de fim não pode ser anterior à data de início."
            return render(request, "adicionar_descanso.html", {
                "descanso": None,
                "tipos_descanso": tipos_descanso,
                "erro": erro,
                "is_edit": False,
            })

        data = {
            "servidor_id": servidor_id,
            "tipo": tipo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "observacao": observacao,
        }

        try:
            supabase.table("descansos").insert(data).execute()
            return redirect("lista_servidores_ativos")
        except Exception as e:
            erro = f"Erro ao cadastrar: {e}"

    return render(request, "adicionar_descanso.html", {
        "descanso": None,
        "tipos_descanso": tipos_descanso,
        "erro": erro,
        "is_edit": False,
    })

def editar_descanso(request, descanso_id):
    tipos_descanso = [
        "Férias", "Folga Compensatória", "Atestado", "Afastamento", "Licença", "Outros"
    ]
    erro = ""
    resp = supabase.table("descansos").select("*").eq("id", descanso_id).single().execute()
    descanso = resp.data
    if not descanso:
        return redirect('lista_servidores_ativos')

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        data_inicio = request.POST.get("data_inicio")
        data_fim = request.POST.get("data_fim")
        observacao = request.POST.get("observacao")

        if data_inicio and data_fim and data_fim < data_inicio:
            erro = "A data de fim não pode ser anterior à data de início."
            return render(request, "adicionar_descanso.html", {
                "descanso": descanso,
                "tipos_descanso": tipos_descanso,
                "erro": erro,
                "is_edit": True,
            })

        supabase.table("descansos").update({
            "tipo": tipo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "observacao": observacao
        }).eq("id", descanso_id).execute()
        return redirect('lista_servidores_ativos')

    return render(request, "adicionar_descanso.html", {
        "descanso": descanso,
        "tipos_descanso": tipos_descanso,
        "erro": erro,
        "is_edit": True,
    })

def excluir_descanso(request, descanso_id):
    if request.method == "POST":
        supabase.table("descansos").delete().eq("id", descanso_id).execute()
        return redirect('lista_servidores_ativos')
    return redirect('lista_servidores_ativos')

def servidores_em_descanso_na_data(request):
    data = request.GET.get("data")
    unidade_id = int(request.GET.get("unidade_id", 1))
    if not data:
        return JsonResponse([], safe=False)
    # Busca todos os servidores ativos da unidade
    servidores = (
        supabase.table("servidores")
        .select("id, nome")
        .eq("status", "Ativo")
        .eq("unidade_id", unidade_id)
        .execute()
        .data
    )
    servidor_ids = [s["id"] for s in servidores]
    # Busca descansos só dos servidores da unidade
    descansos = (
        supabase.table("descansos")
        .select("*")
        .in_("servidor_id", servidor_ids)
        .execute()
        .data
    )
    resultado = []
    data_dt = datetime.strptime(data, "%Y-%m-%d").date()
    for descanso in descansos:
        ini = datetime.strptime(descanso["data_inicio"], "%Y-%m-%d").date()
        fim = datetime.strptime(descanso["data_fim"], "%Y-%m-%d").date()
        if ini <= data_dt <= fim:
            servidor = next((s for s in servidores if s["id"] == descanso["servidor_id"]), None)
            if servidor:
                resultado.append({
                    "id": servidor["id"],      # <-- aqui!
                    "nome": servidor["nome"],
                    "tipo_descanso": descanso["tipo"]
                })
    return JsonResponse(resultado, safe=False)


def descansos_na_semana(request):
    unidade_id = int(request.GET.get("unidade_id", 1))
    semana_idx = int(request.GET.get("semana", 0))
    ano = int(request.GET.get("ano"))
    mes = int(request.GET.get("mes"))

    # calcula as datas da semana com base no mês e índice
    from calendar import monthrange
    from datetime import date

    primeiro_dia = date(ano, mes, 1)
    semanas = []
    dt = primeiro_dia
    while dt.month == mes:
        ini = dt
        fim = ini + timedelta(days=6 - ini.weekday())
        if fim.month != mes:
            fim = date(ano, mes, monthrange(ano, mes)[1])
        semanas.append((ini, fim))
        dt = fim + timedelta(days=1)

    if semana_idx >= len(semanas):
        return JsonResponse([], safe=False)

    ini_semana, fim_semana = semanas[semana_idx]

    # busca servidores ativos
    servidores = supabase.table("servidores") \
        .select("id, nome") \
        .eq("status", "Ativo") \
        .eq("unidade_id", unidade_id) \
        .execute().data

    servidor_ids = [s["id"] for s in servidores]

    descansos = supabase.table("descansos") \
        .select("*") \
        .in_("servidor_id", servidor_ids) \
        .execute().data

    resultado = []
    for d in descansos:
        ini = datetime.strptime(d["data_inicio"], "%Y-%m-%d").date()
        fim = datetime.strptime(d["data_fim"], "%Y-%m-%d").date()
        if fim < ini_semana or ini > fim_semana:
            continue
        servidor = next((s for s in servidores if s["id"] == d["servidor_id"]), None)
        if servidor:
            resultado.append({
                "nome": servidor["nome"],
                "tipo_descanso": d["tipo"]
            })

    return JsonResponse(resultado, safe=False)
def descansos_do_mes(request):
    unidade_id = int(request.GET.get("unidade_id", 1))
    ano = int(request.GET.get("ano"))
    mes = int(request.GET.get("mes"))

    # busca servidores ativos
    servidores = supabase.table("servidores") \
        .select("id, nome") \
        .eq("status", "Ativo") \
        .eq("unidade_id", unidade_id) \
        .execute().data

    servidor_ids = [s["id"] for s in servidores]

    descansos = supabase.table("descansos") \
        .select("*") \
        .in_("servidor_id", servidor_ids) \
        .execute().data

    resultado = []
    for d in descansos:
        ini = datetime.strptime(d["data_inicio"], "%Y-%m-%d").date()
        fim = datetime.strptime(d["data_fim"], "%Y-%m-%d").date()
        if ini.year == ano and ini.month == mes or fim.year == ano and fim.month == mes:
            servidor = next((s for s in servidores if s["id"] == d["servidor_id"]), None)
            if servidor:
                resultado.append({
                    "nome": servidor["nome"],
                    "tipo_descanso": d["tipo"]
                })

    return JsonResponse(resultado, safe=False)