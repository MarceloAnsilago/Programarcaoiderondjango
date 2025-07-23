from django.shortcuts import render
from .forms import ServidorForm
from django.http import HttpResponse
from django.shortcuts import render
from supabase import create_client, Client
from django.shortcuts import redirect
from django.http import JsonResponse
# Create your views here.

SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"  # Pegue em Settings > API > anon/public
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def pagina_servidores(request):
    mensagem = ""
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        matricula = request.POST.get("matricula")
        cargo = request.POST.get("cargo")
        status = "Ativo"
        unidade_id = 1  # Você pode trocar depois para o da unidade logada

        # Envia para o Supabase
        data = {
            "nome": nome,
            "telefone": telefone,
            "matricula": matricula,
            "cargo": cargo,
            "status": status,
            "unidade_id": unidade_id
        }
        try:
            response = supabase.table("servidores").insert(data).execute()
            mensagem = "Servidor cadastrado com sucesso!"
        except Exception as e:
            mensagem = f"Erro ao cadastrar: {e}"

    # Busca todos os servidores para listar (opcional, se quiser mostrar abaixo do form)
    servidores = supabase.table("servidores").select("*").execute().data

    return render(request, "pagina_servidores.html", {
        "mensagem": mensagem,
        "servidores": servidores
    })



def excluir_servidor(request, servidor_id):
    if request.method == "POST":
        supabase.table("servidores").delete().eq("id", servidor_id).execute()
    return redirect("pagina_servidores")

def editar_servidor(request, servidor_id):
    # Busca o servidor atual pelo ID
    response = supabase.table("servidores").select("*").eq("id", servidor_id).single().execute()
    servidor = response.data

    if not servidor:
        return render(request, "editar_servidor.html", {"erro": "Servidor não encontrado."})

    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        cargo = request.POST.get("cargo")
        matricula = request.POST.get("matricula")

        # Atualiza os dados no Supabase
        try:
            supabase.table("servidores").update({
                "nome": nome,
                "telefone": telefone,
                "cargo": cargo,
                "matricula": matricula,
            }).eq("id", servidor_id).execute()
            return redirect("pagina_servidores")
        except Exception as e:
            return render(request, "editar_servidor.html", {"servidor": servidor, "erro": f"Erro ao atualizar: {e}"})

    return render(request, "editar_servidor.html", {"servidor": servidor})

def servidores_ativos(request):
    unidade_id = request.GET.get("unidade_id")  # ou defina fixo, ex: 1
    status = "Ativo"
    servidores = (
        supabase.table("servidores")
        .select("id, nome, telefone")   # <-- Adicione telefone aqui!
        .eq("status", status)
        .eq("unidade_id", unidade_id)
        .execute()
        .data
    )
    return JsonResponse(servidores, safe=False)