from django.shortcuts import render
from supabase import create_client, Client
from django.shortcuts import redirect
from django.http import JsonResponse


SUPABASE_URL = "https://pqhzafiucqqevbnsgwcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxaHphZml1Y3FxZXZibnNnd2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MjQ1MDksImV4cCI6MjA2NjMwMDUwOX0.VOhtsri0IiQgLdGpTCZqZZe_aufHhbOlDx4GqkYMy0M"  # Pegue em Settings > API > anon/public
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Create your views here.

def pagina_veiculos(request):
    mensagem = ""
    if request.method == "POST":
        modelo = request.POST.get("modelo")
        placa = request.POST.get("placa")
        status = request.POST.get("status", "Ativo")
        unidade_id = 1  # Ajuste depois para o usuário logado
        data = {
            "modelo": modelo,
            "placa": placa,
            "status": status,
            "unidade_id": unidade_id
        }
        try:
            supabase.table("veiculos").insert(data).execute()
            mensagem = "Veículo cadastrado com sucesso!"
        except Exception as e:
            mensagem = f"Erro ao cadastrar: {e}"
    veiculos = supabase.table("veiculos").select("*").execute().data
    return render(request, "pagina_veiculos.html", {"mensagem": mensagem, "veiculos": veiculos})

def excluir_veiculos(request, id):
    if request.method == "POST":
        supabase.table("veiculos").delete().eq("id", id).execute()
    return redirect("pagina_veiculos")

def editar_veiculos(request, id):
    veiculo = supabase.table("veiculos").select("*").eq("id", id).single().execute().data
    erro = ""
    if request.method == "POST":
        modelo = request.POST.get("modelo")
        placa = request.POST.get("placa")
        status = request.POST.get("status")
        data = {
            "modelo": modelo,
            "placa": placa,
            "status": status
        }
        try:
            supabase.table("veiculos").update(data).eq("id", id).execute()
            return redirect("pagina_veiculos")
        except Exception as e:
            erro = f"Erro ao editar: {e}"
    return render(request, "editar_veiculos.html", {"veiculo": veiculo, "erro": erro})


def veiculos_ativos(request):
    unidade_id = request.GET.get("unidade_id", 1)  # Valor padrão para teste
    status = "Ativo"
    veiculos = (
        supabase.table("veiculos")
        .select("id, modelo, placa")
        .eq("status", status)
        .eq("unidade_id", unidade_id)
        .execute()
        .data
    )
    return JsonResponse(veiculos, safe=False)