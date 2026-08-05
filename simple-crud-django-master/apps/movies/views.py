import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Movies, Categories,SolicitudDevolucion 
from .forms import MoviesForm, LoginForm


def role_based_redirect(user):
    # Obtenemos el rol de forma segura desde el perfil
    user_role = getattr(getattr(user, 'profile', None), 'role', None)

    # Redirigimos según el rol registrado en la base de datos
    if user.is_superuser or user.is_staff or user_role == 'administrador':
        return redirect('movies:panel-administrador')
        
    elif user_role == 'operador_logistica':
        return redirect('movies:panel-operador-logistica')
        
    elif user_role == 'ejecutivo_logistica':
        return redirect('movies:panel-ejecutivo-logistica')
        
    elif user_role == 'postventa':
        return redirect('movies:panel-postventa')
        
    else:
        return redirect('movies:panel-cliente')
    
def log_in(request):
    # Diccionario que almacena los datos que enviamos a la vista
    form = LoginForm(
        request.POST or None
    )
    context = {'message': None, 'form': form}
    if request.POST and form.is_valid():
        # Verificar credenciales
        # Devuelve un objeto User si las credenciales son válidas.
        # Si las credenciales no son válidas, devuelve None
        user = authenticate(**form.cleaned_data)
        if user is not None:
            # Verificar si el usuario esta activo
            if user.is_active:
                # Adjuntar usuario autenticado a la sesión actual
                login(request, user)
                # Redireccionar a una vista utilizando el nombre de la url
                return role_based_redirect(user)
            else:
                context['message'] = 'El usuario ha sido desactivado'
        else:
            context['message'] = 'Usuario o contraseña incorrecta'
    return render(request, 'movies/login.html', context)


# decorador para restringir el acceso a solo usuarios autenticados
@login_required
def log_out(request):
    logout(request)
    return redirect('movies:log-in')


@login_required
def movie_list(request):
    # CAMBIA ESTO: movies = Movies.objects.all()
    # POR ESTO:
    movies = Movies.objects.filter(user=request.user)
    return render(request, 'movies/index.html', {'movies': movies})


@login_required
def movie_detail(request, pk):
    try:
        # recuperamos el objeto mediante la
        # API de abstracción de base de datos
        # que ofrece Django
        m = Movies.objects.get(pk=pk)
    except Movies.DoesNotExist:
        raise Http404("Esta pelicuala no existe")

    # version con shortcuts de django, equivalente al codigo anterior
    # m = get_object_or_404(Movies, pk=pk)
    return render(request, 'movies/detail.html', {'movie': m})


@login_required
def movie_create(request, **kwargs):
    # Intanciamos la clase form
    # si el diccionario request.POST no esta vacio
    # la instancia se creara con dichos datos, sino estara vacia
    form = MoviesForm(
        request.POST or None,
        request.FILES or None
    )
    # Comprobamos que la peticion es del motodo POST
    # y que el formulario es valido
    if request.POST and form.is_valid():
        # Creamos el objeto sin guardarlo todavía en la base de datos
        movie = form.save(commit=False)
        # Le asignamos el usuario actual que inició sesión
        movie.user = request.user
        # Guardamos definitivamente el registro con su usuario asociado
        movie.save()
        # redirigir a una nueva URL
        return redirect('movies:home')
    return render(request, 'movies/form.html', {'form': form})


@login_required
def movie_update(request, **kwargs):
    # recuperamos el objeto a actualizar
    movie = Movies.objects.get(pk=kwargs.get('pk'))
    # inicializamos el formulario con el objeto recuperado
    form = MoviesForm(
        request.POST or None,
        instance=movie
    )
    if request.POST and form.is_valid():
        form.save()
        return redirect('movies:home')
    return render(request, 'movies/form.html', {'form': form})


@login_required
def movie_delete(request, **kwargs):
    # Solo el Administrador puede eliminar registros
    if hasattr(request.user, 'profile') and request.user.profile.role != 'administrador':
        return redirect('movies:home')

    movie = Movies.objects.get(pk=kwargs.get('pk'))
    movie.delete()
    return redirect('movies:home')


@login_required
def category_list(request):
    categories = Categories.objects.all()
    return render(request, 'movies/category/category_list.html', {'categories': categories})

# Vista exclusiva para Administrador (Generar reportes)
@login_required
def reportes_view(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'administrador':
        return redirect('movies:home')
    
    # Calculamos los indicadores reales desde la base de datos
    total_solicitudes = SolicitudDevolucion.objects.count()
    completadas = SolicitudDevolucion.objects.filter(estado__iexact='Completado').count()
    pendientes = SolicitudDevolucion.objects.exclude(estado__iexact='Completado').count()

    context = {
        'total_solicitudes': total_solicitudes,
        'completadas': completadas,
        'pendientes': pendientes,
    }
    return render(request, 'movies/reportes.html', context)

# --- PANEL DE POSTVENTA ---
@login_required
def panel_postventa(request):
    # Verificamos que el usuario sea postventa o administrador
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'postventa' and user_role != 'administrador':
        return redirect('movies:home')
    
    # Aquí puedes agregar la lógica para revisar solicitudes (ej: solicitudes = Solicitud.objects.all())
    return render(request, 'movies/panel_postventa.html')


# --- PANEL DE EJECUTIVO DE LOGÍSTICA ---
@login_required
def panel_ejecutivo_logistica(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'ejecutivo_logistica' and user_role != 'administrador':
        return redirect('movies:home')
        
    return render(request, 'movies/panel_ejecutivo_logistica.html')

# --- PANEL DE OPERADOR DE LOGÍSTICA ---
@login_required
def panel_operador_logistica(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'operador_logistica' and user_role != 'administrador':
        return redirect('movies:home')
        
    return render(request, 'movies/panel_operador_logistica.html')

# --- 1. SEGUIMIENTO DE LA OPERACIÓN LOGÍSTICA (Panel Principal) ---
@login_required
def panel_ejecutivo_logistica(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'ejecutivo_logistica' and user_role != 'administrador':
        return redirect('movies:home')
    
    return render(request, 'movies/panel_ejecutivo_logistica.html')


# --- 2. COORDINAR RETIROS ---
@login_required
def coordinar_retiros(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'ejecutivo_logistica' and user_role != 'administrador':
        return redirect('movies:home')
    
    # Filtrar solo las solicitudes aprobadas para que logística pueda coordinar el retiro
    solicitudes = SolicitudDevolucion.objects.filter(estado__iexact='aprobada').order_by('-fecha_creacion')
    
    return render(request, 'movies/coordinar_retiros.html', {'solicitudes': solicitudes})

# --- 2. solicitud coordinacion---
@login_required
def coordinar_retiro_accion(request, solicitud_id):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'ejecutivo_logistica' and user_role != 'administrador':
        return redirect('movies:home')
    
    solicitud = get_object_or_404(SolicitudDevolucion, id=solicitud_id)
    
    # Actualizamos el estado para que avance el flujo logístico
    solicitud.estado = 'Retiro Coordinado'
    solicitud.save()
    
    return redirect('movies:coordinar_retiros') # Reemplaza por el name de la url de esta vista si es distinto


# --- 3. GENERAR ETIQUETAS DE NUEVO ENVÍO ---
@login_required
def generar_etiqueta(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'ejecutivo_logistica' and user_role != 'administrador':
        return redirect('movies:home')
    
    # Filtrar las solicitudes con retiro coordinado para poder generarles etiqueta
    solicitudes = SolicitudDevolucion.objects.filter(estado__iexact='Retiro Coordinado').order_by('-fecha_creacion')
    
    return render(request, 'movies/generar_etiqueta.html', {'solicitudes': solicitudes})

# --- 3. GENERAR ETIQUETAS accion ---
@login_required
def generar_etiqueta_accion(request, solicitud_id):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'ejecutivo_logistica' and user_role != 'administrador':
        return redirect('movies:home')
    
    solicitud = get_object_or_404(SolicitudDevolucion, id=solicitud_id)
    
    # Actualizamos el estado para que avance el flujo logístico
    solicitud.estado = 'Etiqueta Generada'
    solicitud.save()
    
    return redirect('movies:generar_etiqueta')


# --- 1. REVISAR SOLICITUDES ---
@login_required
def revisar_solicitudes(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'postventa' and user_role != 'administrador':
        return redirect('movies:home')
    
    solicitudes = SolicitudDevolucion.objects.all().order_by('-fecha_creacion')
    return render(request, 'movies/revisar_solicitudes.html', {'solicitudes': solicitudes})


# --- 2. VALIDAR EVIDENCIA ---
@login_required
def validar_evidencia(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'postventa' and user_role != 'administrador':
        return redirect('movies:home')
        
    solicitudes = SolicitudDevolucion.objects.all().order_by('-fecha_creacion')
    return render(request, 'movies/validar_evidencia.html', {'solicitudes': solicitudes})


# --- 3. AUTORIZAR DEVOLUCIONES O CAMBIOS ---
@login_required
def autorizar_devoluciones(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'postventa' and user_role != 'administrador':
        return redirect('movies:home')
    
    # Usar 'Pendiente' con la P mayúscula tal como se ve en tu interfaz
    solicitudes = SolicitudDevolucion.objects.filter(estado='Pendiente').order_by('-fecha_creacion')
    return render(request, 'movies/autorizar_devoluciones.html', {'solicitudes': solicitudes})
# --- 3. Aprobar ------
@login_required
def aprobar_devolucion(request, pk):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'postventa' and user_role != 'administrador':
        return redirect('movies:home')
    
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudDevolucion, pk=pk)
        solicitud.estado = 'aprobada'  # O el nombre de tu campo de estado
        solicitud.save()
    return redirect('movies:autorizar_devoluciones')

# --- 3. Rechazar---
@login_required
def rechazar_devolucion(request, pk):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'postventa' and user_role != 'administrador':
        return redirect('movies:home')
    
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudDevolucion, pk=pk)
        solicitud.estado = 'rechazada' # O el nombre de tu campo de estado
        solicitud.save()
    return redirect('movies:autorizar_devoluciones')


# --- 1. EJECUTAR RETIROS Y ENVÍOS ---
@login_required
def ejecutar_retiros_envios(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'operador_logistica' and user_role != 'administrador':
        return redirect('movies:home')
    
    # Filtrar las solicitudes que tienen la etiqueta generada listas para la ejecución
    solicitudes = SolicitudDevolucion.objects.filter(estado__iexact='Etiqueta Generada').order_by('-fecha_creacion')
    
    return render(request, 'movies/ejecutar_retiros_envios.html', {'solicitudes': solicitudes})

# --- 1. EJECUTAR RETIROS Y ENVÍOS  accion---
@login_required
def ejecutar_retiros_envios_accion(request, solicitud_id):
    # Si quieres evitar que te bote al home por temas de roles mientras pruebas:
    # (puedes quitar la validación estricta de roles temporalmente)
    
    solicitud = get_object_or_404(SolicitudDevolucion, id=solicitud_id)
    
    # Actualizamos el estado al cierre definitivo del proceso
    solicitud.estado = 'Completado'
    solicitud.save()
    
    # Te devuelve exactamente a la lista de ejecución que querías
    return redirect('movies:ejecutar_retiros_envios')

# --- PANEL DE ADMINISTRADOR ---
@login_required
def panel_administrador(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'administrador':
        return redirect('movies:home')
    
    # Indicadores de Logística Inversa
    total_solicitudes = SolicitudDevolucion.objects.count()
    completadas = SolicitudDevolucion.objects.filter(estado__iexact='Completado').count()
    pendientes = SolicitudDevolucion.objects.exclude(estado__iexact='Completado').count()

    context = {
        'total_solicitudes': total_solicitudes,
        'completadas': completadas,
        'pendientes': pendientes,
    }
    return render(request, 'movies/panel_administrador.html', context)

@login_required
def panel_base_datos(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'administrador':
        return redirect('movies:home')
    
    # Obtenemos las solicitudes de devolución para visualizarlas en el panel
    solicitudes = SolicitudDevolucion.objects.all().order_by('-fecha_creacion')
    
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'movies/panel_base_datos.html', context)

@login_required
def crear_solicitud(request):
    """Permite al cliente iniciar una solicitud y adjuntar evidencia."""
    if request.method == 'POST':
        producto = request.POST.get('producto')
        motivo = request.POST.get('motivo')
        evidencia = request.FILES.get('evidencia')

        SolicitudDevolucion.objects.create(
            usuario=request.user,
            producto=producto,
            motivo=motivo,
            evidencia=evidencia
        )
        return redirect('movies:panel-cliente')

    return render(request, 'movies/crear_solicitud.html')

@login_required
def consultar_estado_solicitudes(request):
    """Permite al cliente consultar el estado de sus solicitudes."""
    solicitudes = SolicitudDevolucion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'movies/consultar_estado.html', {'solicitudes': solicitudes})

@login_required
def panel_cliente(request):
    """Panel principal exclusivo para clientes."""
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    # Si es personal interno por error cae aquí, los mandamos a su home o admin, 
    # pero los clientes puros entran directo a su panel.
    return render(request, 'movies/panel_cliente.html')

@login_required
def descargar_reporte(request):
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not request.user.is_superuser and user_role != 'administrador':
        return redirect('movies:home')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_logistica_inversa.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Producto', 'Motivo', 'Estado', 'Fecha de Creacion'])

    solicitudes = SolicitudDevolucion.objects.all().order_by('-fecha_creacion')
    for item in solicitudes:
        writer.writerow([item.id, item.producto, item.motivo, item.estado, item.fecha_creacion])

    return response