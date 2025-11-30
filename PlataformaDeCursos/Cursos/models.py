from django.db import models
from django.contrib.auth.models import User

# Create your models here.
  #  ---- MODELOS DE LA APLICACION ----
from django.db import models

class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #Relacion de usuario para que el maestro tenga una sesion igual al estudiante
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Inscripcion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    nombre_estudiante = models.CharField(max_length=100)
    email_estudiante = models.EmailField()
    fecha_inscripcion = models.DateField(auto_now_add=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username if self.user else self.nombre_estudiante} - {self.curso.titulo}"
    
    def porcentaje_asistencia(self):
        total_sesiones = self.curso.sesiones.count()
        asistencias = Asistencia.objects.filter(inscripcion=self, presente=True).count()
        if total_sesiones == 0:
            return 0
        return (asistencias * 100) / total_sesiones
    
    def tiene_certificado(self, minimo=80):
        return self.porcentaje_asistencia() >= minimo

class Recurso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_archivo = models.CharField(max_length=50)
    enlace = models.URLField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Progreso(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.inscripcion.nombre_estudiante} - {self.recurso.titulo}"

 # Modelo para el material extra de los cursos
class MaterialExtra(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100) 
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='materiales/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
# Modelo para un perfil mas profesional del profesor o estudiante
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='static/perfiles/', default='static/perfiles/perfil_defecto.jpg')
    biografia = models.TextField(blank=True, null=True)
    idioma_nativo = models.CharField(max_length=50, blank=True, null=True)
    intereses = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Sesion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='sesiones')
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    def __str__(self):
        return f"{self.titulo} - {self.curso.titulo}"
    
class Asistencia(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE)
    presente = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.inscripcion.nombre_estudiante} - {self.sesion.titulo}"
    
class Certificado(models.Model):
    inscripcion = models.OneToOneField(Inscripcion, on_delete=models.CASCADE)
    porcentaje_asistencia = models.FloatField()
    fecha_emision = models.DateField(auto_now_add=True)
    archivo = models.FileField(upload_to='cetificados/', blank=True, null=True)
    def __str__(self):
        return f"Certificado - {self.inscripcion.nombre_estudiante}"