from django.shortcuts import render, redirect
from django.http import JsonResponse
from supabase import create_client
from urllib.parse import quote_plus
from django.http import JsonResponse, HttpResponse

SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def pagina_atividades(request):
    mensagem = ""
    unidade_id = 1  # Pode vir da sessão futuramente

    exibir_inativos = request.GET.get("inativos") == "on"
    termo_busca = request.GET.get("busca", "").strip()

    # Cadastro
    if request.method == "POST":
        nome = request.POST.get("nome")
        classificacao = request.POST.get("classificacao")
        status = request.POST.get("status", "Ativo")
        data = {
            "nome": nome,
            "classificacao": classificacao,
            "status": status,
            "unidade_id": unidade_id
        }

        try:
            # Garante que "Expediente Administrativo" exista
            expediente = supabase.table("atividades") \
                .select("*") \
                .eq("nome", "Expediente Administrativo") \
                .eq("unidade_id", unidade_id) \
                .single() \
                .execute()
        except Exception:
            expediente = None

        if not expediente or not expediente.data:
            try:
                supabase.table("atividades").insert({
                    "nome": "Expediente Administrativo",
                    "classificacao": "Padrão",
                    "status": "Ativo",
                    "unidade_id": unidade_id
                }).execute()
            except Exception as e:
                print("Erro ao criar atividade padrão:", e)

        try:
            supabase.table("atividades").insert(data).execute()
            mensagem = "Atividade cadastrada com sucesso!"
        except Exception as e:
            mensagem = f"Erro ao cadastrar: {e}"

    # 🔍 Listagem e Filtro
    try:
        query = supabase.table("atividades").select("*")
        status_filtro = "Inativo" if exibir_inativos else "Ativo"
        query = query.eq("status", status_filtro).eq("unidade_id", unidade_id)

        if termo_busca and len(termo_busca) >= 2:
            query = query.or_(
                f"nome.ilike.*{termo_busca}*,classificacao.ilike.*{termo_busca}*"
            )

        atividades = query.order("id", desc=True).execute().data
    except Exception as e:
        return HttpResponse(f"<h3>❌ ERRO ao buscar atividades:</h3><pre>{e}</pre>", status=500)

    return render(request, "pagina_atividades.html", {
        "mensagem": mensagem,
        "atividades": atividades,
        "termo_busca": termo_busca,
        "exibir_inativos": exibir_inativos
    })

def inativar_atividade(request, id):
    if request.method == "POST":
        supabase.table("atividades").update({"status": "Inativo"}).eq("id", id).execute()
    return redirect("pagina_atividades")


def reativar_atividade(request, id):
    if request.method == "POST":
        supabase.table("atividades").update({"status": "Ativo"}).eq("id", id).execute()
    return redirect("pagina_atividades")

def editar_atividade(request, id):
    atividade = supabase.table("atividades").select("*").eq("id", id).single().execute().data
    erro = ""
    if request.method == "POST":
        nome = request.POST.get("nome")
        classificacao = request.POST.get("classificacao")
        status = request.POST.get("status")
        data = {
            "nome": nome,
            "classificacao": classificacao,
            "status": status,
            "unidade_id": atividade['unidade_id']  # mantém unidade original
        }
        try:
            supabase.table("atividades").update(data).eq("id", id).execute()
            return redirect("pagina_atividades")
        except Exception as e:
            erro = f"Erro ao editar: {e}"
    return render(request, "editar_atividades.html", {"atividade": atividade, "erro": erro})

def atividades_ativas(request):
    unidade_id = request.GET.get("unidade_id", 1)  # Valor padrão para teste
    status = "Ativo"
    atividades = (
        supabase.table("atividades")
        .select("id, nome")
        .eq("status", status)
        .eq("unidade_id", unidade_id)
        .execute()
        .data
    )
    return JsonResponse(atividades, safe=False)
