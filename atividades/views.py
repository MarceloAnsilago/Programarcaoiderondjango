from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from supabase import create_client

SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def pagina_atividades(request):
    mensagem = ""
    if request.method == "POST":
        nome = request.POST.get("nome")
        classificacao = request.POST.get("classificacao")
        status = request.POST.get("status", "Ativo")
        data = {
            "nome": nome,
            "classificacao": classificacao,
            "status": status
        }
        try:
            supabase.table("atividades").insert(data).execute()
            mensagem = "Atividade cadastrada com sucesso!"
        except Exception as e:
            mensagem = f"Erro ao cadastrar: {e}"
    atividades = supabase.table("atividades").select("*").execute().data
    return render(request, "pagina_atividades.html", {"mensagem": mensagem, "atividades": atividades})

def excluir_atividade(request, id):
    if request.method == "POST":
        supabase.table("atividades").delete().eq("id", id).execute()
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
            "status": status
        }
        try:
            supabase.table("atividades").update(data).eq("id", id).execute()
            return redirect("pagina_atividades")
        except Exception as e:
            erro = f"Erro ao editar: {e}"
    return render(request, "editar_atividades.html", {"atividade": atividade, "erro": erro})

