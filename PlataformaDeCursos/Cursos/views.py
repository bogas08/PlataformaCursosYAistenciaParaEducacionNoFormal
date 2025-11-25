from datetime import date
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from .forms import EditarPerfilForm,InscripcionForm,MaterialExtraForm,PerfilForm,RegistroUsuarioForm
from .models import Curso, Inscripcion, MaterialExtra, Perfil, Profesor, Progreso, Recurso

# Create your views here.
# Verifica si el usuario tiene asociado un profesor para inicio de Sesion y redirecciones
@login_required
def login_redirect(request):
    if hasattr(request.user, 'profesor'):
        return redirect('dashboard')
    else:
        return redirect('lista_cursos')

# Lista de los cursos en la pagina principal
def lista_cursos(request):
    cursos = Curso.objects.all()
    cursos_inscritos_ids = []
    
    # Verficia si el usuario ya se encuentra inscrito a la materia
    if request.user.is_authenticated:
        cursos_inscritos_ids = Inscripcion.objects.filter(user=request.user).values_list('curso_id', flat=True)

    return render(request, 'cursos/cursos.html', {
        'cursos': cursos,
        'cursos_inscritos_ids': cursos_inscritos_ids
    })

# muesta a detalles las fehas de inicio y fin como tambien los usuarios inscritos en cada curso

@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripciones = Inscripcion.objects.filter(curso=curso)
    es_profesor = hasattr(request.user, 'profesor')
    
    # verifica si  el usuario inscrito en este curso
    esta_inscrito = Inscripcion.objects.filter(user=request.user, curso=curso).exists() if request.user.is_authenticated else False

    return render(request, 'cursos/detalle_Cursos.html', {
        'curso': curso,
        'inscripciones': inscripciones,
        'es_profesor': es_profesor,
        'esta_inscrito': esta_inscrito
    })


# PRIMER FUNCIONALIDAD IMPLEMENTADA
# Inscripción de un usuario a un curso
# requiriendo el login del usuario
@login_required
def inscribirse_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    user = request.user
    
    # Evita que un profesor se inscriba
    if hasattr(request.user, 'profesor'):
        messages.error(request, "Los profesores no pueden inscribirse.")
        return redirect('lista_cursos')
    
    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            inscripcion, created = Inscripcion.objects.get_or_create(
                user=user,
                curso=curso,
                defaults={
                    'nombre_estudiante': form.cleaned_data['nombre_estudiante'],
                    'email_estudiante': form.cleaned_data['email_estudiante'],
                }
            )
            messages.success(request, '¡Te has inscrito correctamente al curso!')
            if not created:
                # Si ya existe manda este mensaje de error
                form.add_error(None, 'Ya estás inscrito en este curso.')
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = InscripcionForm(initial={
            'nombre_estudiante': user.get_full_name() or user.username,
            'email_estudiante': user.email
        })

    return render(request, 'cursos/inscribirse_curso.html', {
        'curso': curso,
        'form': form
    })
    
# SEGUNDA FUNCIONALIDAD IMPLEMENTADA
# SUBIR UN MATERIAL EXTRA
# requiriendo el loggin solo del maestro encargado de la materia

def subir_material_extra(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        form = MaterialExtraForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.curso = curso
            material.profesor = Profesor.objects.get(user=request.user)
            material.save()

            # 🔥 Crear Recurso automáticamente
            Recurso.objects.create(
                titulo=material.titulo,
                descripcion=material.descripcion,
                tipo_archivo="Archivo",
                enlace=material.archivo.url,
                curso=curso
            )

            return redirect('subir_material_extra', curso_id=curso.id)
    else:
        form = MaterialExtraForm()

    material_extra = MaterialExtra.objects.filter(curso=curso)

    return render(request, 'cursos/subir_material_extra.html', {
        'curso': curso,
        'form': form,
        'material_extra': material_extra,
    })
    
# Eliminar material extra
@login_required
def eliminar_material_extra(request, material_id):
    material = get_object_or_404(MaterialExtra, id=material_id)

    if material.profesor.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este material.")

    curso_id = material.curso.id
    
    Recurso.objects.filter(titulo=material.titulo, curso=material.curso).delete()

    material.archivo.delete()  # Borra el archivo en materiales
    material.delete()  # Borra en la base de datos

    messages.error(request, "Material eliminado correctamente.")
    return redirect('subir_material_extra', curso_id=curso_id)


#  VISTA PARA QUE CUALQUIER USUARIO SE PUEDA INSCRIBIR A UN CURSO (evitar al maestro) 
def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_cursos')
    else:
        form = RegistroUsuarioForm()
    return render(request, "registration/registro.html", {"form": form})


# TERCERA FUNCIONALIDAD IMPLEMENTADA
# progreso del estudiante.
# permite al estudiante completar recursos de materias inscritas y verlos en tiempo real
@login_required
def progreso_estudiante(request):
    usuario = request.user
    inscripciones = Inscripcion.objects.filter(user=usuario)
    
    progresos = Progreso.objects.filter(inscripcion__in=inscripciones).select_related('recurso', 'inscripcion', 'inscripcion__curso')

    progreso_por_curso = {}
    for inscripcion in inscripciones:
        recursos = Recurso.objects.filter(curso=inscripcion.curso)
        completados = progresos.filter(inscripcion=inscripcion, completado=True).count()
        total = recursos.count()
        porcentaje = (completados / total * 100) if total > 0 else 0
        progreso_por_curso[inscripcion.curso.id] = {
            'curso': inscripcion.curso,
            'porcentaje': round(porcentaje, 2),
            'total': total,
            'completados': completados,
            'recursos': recursos,
            'completados_ids': list(progresos.filter(inscripcion=inscripcion, completado=True).values_list('recurso_id', flat=True))
        }
    return render(request, 'cursos/progreso_estudiante.html', {
        'progreso_por_curso': progreso_por_curso
    })

# Ver un recurso ya creado
@login_required
def ver_recurso(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id)
    inscripcion = Inscripcion.objects.filter(user=request.user, curso=recurso.curso).first()
    if not inscripcion:
        return HttpResponseForbidden("No estás inscrito en este curso.")

    progreso = Progreso.objects.filter(inscripcion=inscripcion, recurso=recurso).first()
    
    completado = progreso.completado if progreso else False
    return render(request, 'cursos/ver_recurso.html', {
        'recurso': recurso,
        'completado': completado
    })

# Marcar como completado el recurso visto por el estudiante.
@login_required
def marcar_completado(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id)
    inscripcion = Inscripcion.objects.filter(user=request.user, curso=recurso.curso).first()
    if not inscripcion:
        return HttpResponseForbidden("No estás inscrito en este curso.")

    progreso, _ = Progreso.objects.get_or_create(inscripcion=inscripcion, recurso=recurso)
    progreso.completado = True
    progreso.fecha_completado = date.today()
    progreso.save()

    return redirect('ver_recurso', recurso_id=recurso.id)

#EXTRAS
#Darse de baja de curso
from django.contrib import messages

@login_required
def darse_de_baja_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripcion = Inscripcion.objects.filter(user=request.user, curso=curso).first()

    if not inscripcion:
        messages.error(request, "No estás inscrito en este curso.")
        return redirect('detalle_curso', curso_id=curso.id)

    if request.method == 'POST':
        inscripcion.delete()
        messages.error(request, f"Tu inscripción ha sido cancelada: {curso.titulo}.")
        return redirect('lista_cursos')

    return render(request, 'cursos/confirmar_baja.html', {'curso': curso})



#maestro vea a sus estudiantes con el progreso
@login_required
def dashboard(request):
    if hasattr(request.user, 'profesor'):
        profesor = request.user.profesor
        cursos = Curso.objects.filter(profesor=profesor)
        cursos_con_inscripciones = []

        for curso in cursos:
            inscripciones = Inscripcion.objects.filter(curso=curso)

            # Para cada inscripción, obtener progreso de ese estudiante en ese curso
            estudiantes_con_progreso = []
            for inscripcion in inscripciones:
                total_recursos = Recurso.objects.filter(curso=curso).count()
                completados = Progreso.objects.filter(inscripcion=inscripcion, completado=True).count()
                porcentaje = (completados / total_recursos * 100) if total_recursos > 0 else 0

                estudiantes_con_progreso.append({
                    'inscripcion': inscripcion,
                    'progreso': round(porcentaje, 2),
                    'total_recursos': total_recursos,
                    'completados': completados,
                })

            cursos_con_inscripciones.append({
                'curso': curso,
                'estudiantes': estudiantes_con_progreso,
            })

        return render(request, 'cursos/dashboard_profesor.html', {
            'cursos_con_inscripciones': cursos_con_inscripciones
        })
    else:
        return redirect('lista_cursos')

# Funciones y vistas para el perfil de usuario (profesor y estudiante)
# Esto es para ver si el usuario es un profesor y valida
    
def es_profesor(user):
    return hasattr(user, 'profesor')

def perfil_usuario(request):
    user = request.user
    if es_profesor(user): 
        profesor = user.profesor
        cursos = Curso.objects.filter(profesor=profesor)
        perfil = Perfil.objects.filter(user=user).first()
        
        return render(request, 'cursos/perfil_profesor.html', {
            'es_profesor':True,
            'profesor': profesor,
            'perfil': perfil,
            'cursos': cursos
        })
    else:
        
        inscripciones = Inscripcion.objects.filter(user=user)
        cursos_info = []
        progresos = Progreso.objects.filter(inscripcion__in=inscripciones).select_related('recurso', 'inscripcion', 'inscripcion__curso')
        
        for insc in inscripciones:
            recursos = Recurso.objects.filter(curso=insc.curso)
            progreso_dict = {
                p.recurso.id: p.completado
                for p in Progreso.objects.filter(inscripcion=insc)
            }
            materiales = []
            for recurso in recursos:
                estado = 'completado' if progreso_dict.get(recurso.id) else 'incompleto'
                materiales.append({
                    'titulo': recurso.titulo,
                    'estado': estado,
                    'id':recurso.id
                })
            completados = progresos.filter(inscripcion=insc, completado=True).count()
            total = recursos.count()

            porcentaje = round((completados / total * 100), 2) if total > 0 else 0
            cursos_info.append({
                'titulo_curso': insc.curso.titulo,
                'materiales': materiales,
                'porcentaje':porcentaje,
            })
        perfil = Perfil.objects.filter(user=user).first()

        return render(request, 'cursos/perfil_estudiante.html', {
            'es_profesor':False,
            'perfil': perfil, #Enserio hay que poner al medio esta huevada, al medio unicamente funciona (creo)
            'cursos_info': cursos_info
        })

# Edicion de perfil, validando para ambos perfiles
@login_required
def editar_perfil(request):
    user = request.user
    perfil, _ = Perfil.objects.get_or_create(user=user)
    if request.method == 'POST':
        user_form = EditarPerfilForm(request.POST, instance=user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, '¡Perfil del usuario actualizado correctamente!')
            return redirect('perfil_usuario')
    else:
        user_form = EditarPerfilForm(instance=user)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'cursos/editar_perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form
    })

@login_required
def cambio_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Contraseña cambiada correctamente!')
            update_session_auth_hash(request, user)  # Mantiene la sesión activa
            return redirect('perfil_usuario')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'registration/cambio_password.html', {'form': form})
