from django import forms

class ServidorForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}))
    telefone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}))
    cargo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo'}))
    matricula = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula'}))
