from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def pagina_programacao(request):
    return render(request, 'pagina_programacao.html')