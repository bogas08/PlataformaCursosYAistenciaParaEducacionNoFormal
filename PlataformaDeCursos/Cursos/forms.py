from django import forms
from .models import Inscripcion , MaterialExtra, Perfil
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
#   FORMULARIO PARA LA INSCRIPCION DE UN USUARIO A UN CURSO X
class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['nombre_estudiante', 'email_estudiante']
# material extra para los cursos
class MaterialExtraForm(forms.ModelForm):
    class Meta:
        model = MaterialExtra
        fields = ('titulo', 'descripcion', 'archivo')

# REGISTRO PARA QUE CUALQUIER USUARIIO PUEDA CREAR UNA CUENTA E INSCRIBIRSE A UN CURSO
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
# AGREGA UN PERFIL A CUALQUIER USUARIO REGISTRADO
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['imagen', 'biografia', 'idioma_nativo', 'intereses']

#   EDITAR INFORMACION DEL USUARIO CAMPOS COMO NAME_USER Y EMAIL
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            
        }