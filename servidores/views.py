from django.shortcuts import render
from .forms import ServidorForm
from django.http import HttpResponse
# Create your views here.

def pagina_servidores(request):
    form = ServidorForm()
    if request.method == "POST":
        form = ServidorForm(request.POST)
        if form.is_valid():
            # Aqui você salva os dados (banco, lista, etc)
            # Por enquanto só mostra mensagem
            return render(request, 'pagina_servidores.html', {'form': ServidorForm(), 'msg': 'Servidor cadastrado com sucesso!'})
    return render(request, 'pagina_servidores.html', {'form': form})