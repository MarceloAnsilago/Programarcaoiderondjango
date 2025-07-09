from django import forms

class ServidorForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(label="Telefone", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(99) 99999-9999'}))
    cargo = forms.CharField(label="Cargo", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    matricula = forms.CharField(label="Matrícula", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
