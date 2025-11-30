from django.urls import path
from Cursos.views import login_redirect
from . import views

urlpatterns = [
    # path('', views.vistaInicial, name='inicio'),
    # vista inicial, tabla de cursos
    path('', views.lista_cursos, name='lista_cursos'),
    # vista de detalle de cada curso
    path("curso/<int:curso_id>/", views.detalle_curso, name="detalle_curso"),
    # vista para la inscripción a un curso
    path('curso/<int:curso_id>/inscribirse/', views.inscribirse_curso, name='inscribirse_curso'),
     # vista para el registro de un usuario
    path('registro/', views.registro_usuario, name='registro_usuario'), 
    # vista para subir material extra a un curso
    path('curso/<int:curso_id>/subir_material_extra/', views.subir_material_extra, name='subir_material_extra'),
    # vista del progreso de todos los cursos
    path('progreso/', views.progreso_estudiante, name='progreso_estudiante'),
    # vista para ver el recurso
    path('recurso/<int:recurso_id>/', views.ver_recurso, name='ver_recurso'),
    # vista para ver el recurso "completar"
    path('recurso/<int:recurso_id>/completar/', views.marcar_completado, name='marcar_completado'),
    # vista para ver el maestro"
    path('dashboard/', views.dashboard, name='dashboard'),
    # vista para la redireccion entre estudiante y maestro"
    path('redireccion/', login_redirect, name='login_redirect'),
    # vista para darse de baja de la materia inscrita
    path('curso/<int:curso_id>/baja/', views.darse_de_baja_curso, name='darse_de_baja_curso'),
    # vista para perfil de usuario
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    # editar la informacion del usuario
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    # cambiar la contraseña del usuario
    path('cambiar-password/', views.cambio_password, name='cambio_password'),
    # eliminar material_extra
    path('material/<int:material_id>/eliminar/', views.eliminar_material_extra, name='eliminar_material_extra'),
    # nueva sesion por curso
    path('crear_sesion/', views.crear_sesion, name='crear_sesion'),
    # Toma asistencia
    path('asistencia/<int:id_sesion>', views.tomar_asistencia, name='tomar_asistencia'),
    # certificado
    path('certificado/<int:user>', views.certificado, name='certificado'),
    # lista sesiones
    path('lista_sesiones/', views.lista_sesion, name='lista_sesiones')
]



