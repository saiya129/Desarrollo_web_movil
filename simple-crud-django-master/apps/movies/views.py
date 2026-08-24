from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import ProductoInversoForm
from .models import (
    AgendamientoLogistica,
    ImagenProducto,
    PerfilUsuario,
    ProductoInverso,
)


def log_in(request):
    if request.user.is_authenticated:
        return redirect('movies:panel-cliente')

    error = None  # Inicializamos la variable vacía

    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)

        if user is not None:
            login(request, user)
            return redirect('movies:panel-cliente')
        else:
            error = 'Credenciales inválidas'

    return render(request, 'movies/login.html', {'error': error})


@login_required
def log_out(request):
    logout(request)
    return redirect('movies:log-in')


@login_required
def dashboard_principal(request):
    perfil, created = PerfilUsuario.objects.get_or_create(
        user=request.user, defaults={'tipo': 'cliente'}
    )
    if perfil.tipo == 'empresa':
        productos = ProductoInverso.activos.filter(empresa=request.user).prefetch_related('imagenes')
        return render(
            request, 'movies/panel_administrador.html', {'productos': productos}
        )
    else:
        productos_rescate = ProductoInverso.activos.exclude(empresa=request.user).prefetch_related('imagenes')
        return render(
            request,
            'movies/panel_cliente.html',
            {'productos': productos_rescate},
        )


@login_required
def soft_delete_producto(request, pk):
    producto = get_object_or_404(ProductoInverso, pk=pk)
    producto.is_deleted = True
    producto.deleted_at = timezone.now()
    producto.save()
    return redirect('movies:mis-productos')


# --- Vistas para Pestañas, Marketplace y Agendamiento ---


@login_required
def panel_cliente(request):
    # Productos de otros usuarios (excluyendo los subidos por el usuario actual)
    productos_rescate = ProductoInverso.activos.exclude(empresa=request.user).prefetch_related('imagenes')
    
    # Capturar parámetros de búsqueda y filtro por GET
    query = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    
    # Filtrar por texto de búsqueda si existe
    if query:
        productos_rescate = productos_rescate.filter(titulo__icontains=query)
        
    # Filtrar por categoría si existe y no está vacía
    if categoria:
        productos_rescate = productos_rescate.filter(categoria__iexact=categoria)
        
    # --- SISTEMA DE NOTIFICACIONES ---
    # 1. Compras realizadas por ti
    mis_compras_notif = AgendamientoLogistica.objects.filter(
        cliente_empresa=request.user.username
    )
    
    # 2. Ventas de productos que tú publicaste
    mis_productos_ids = ProductoInverso.objects.filter(empresa=request.user).values_list('id', flat=True)
    mis_ventas_notif = AgendamientoLogistica.objects.filter(
        producto_id__in=mis_productos_ids
    )
    
    total_notificaciones_count = mis_compras_notif.count() + mis_ventas_notif.count()

    return render(
        request,
        'movies/panel_cliente.html',
        {
            'productos': productos_rescate,
            'mis_compras_notif': mis_compras_notif,
            'mis_ventas_notif': mis_ventas_notif,
            'notif_count': total_notificaciones_count,
            'request_get': request.GET,
        },
    )


@login_required
def mis_productos(request):
    # Productos publicados por el usuario actual con borrado lógico aplicado y optimización de imágenes
    productos = ProductoInverso.activos.filter(empresa=request.user).prefetch_related('imagenes')
    return render(request, 'movies/mis_productos.html', {'productos': productos})


@login_required
def mis_compras(request):
    # Compras o agendamientos logísticos realizados
    compras = AgendamientoLogistica.objects.filter(
        cliente_empresa=request.user.username
    )
    return render(request, 'movies/mis_compras.html', {'compras': compras})


@login_required
def seguimiento_compra(request, pk):
    # Vista para consultar el detalle logístico de una compra específica
    agendamiento = get_object_or_404(AgendamientoLogistica, pk=pk)
    return render(request, 'movies/seguimiento_compra.html', {'agendamiento': agendamiento})


@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(ProductoInverso, pk=pk)
    return render(request, 'movies/detalle_producto.html', {'producto': producto})


@login_required
def editar_producto(request, pk):
    # Asegura que solo el usuario dueño del producto pueda editarlo
    producto = get_object_or_404(ProductoInverso, pk=pk, empresa=request.user)

    if request.method == 'POST':
        form = ProductoInversoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            prod = form.save()

            # --- PROCESAR EL BORRADO DE IMÁGENES MARCADAS ---
            ids_a_eliminar = request.POST.getlist('eliminar_imagenes')
            if ids_a_eliminar:
                ImagenProducto.objects.filter(id__in=ids_a_eliminar, producto=prod).delete()

            # Procesar nuevas imágenes si el usuario decide adjuntar adicionales
            files = request.FILES.getlist('imagenes')
            if files:
                for index, f in enumerate(files):
                    ImagenProducto.objects.create(
                        producto=prod, imagen=f, es_principal=False
                    )

            # Redirige de vuelta al detalle del producto
            return redirect('movies:detalle-producto', pk=prod.pk)
    else:
        form = ProductoInversoForm(instance=producto)

    return render(request, 'movies/editar_producto.html', {'form': form, 'producto': producto})


@login_required
def agendar_retiro_producto(request, pk):
    producto = get_object_or_404(ProductoInverso, pk=pk)
    
    # Capturar la cantidad enviada por GET (desde el detalle) o POST (si ya está en el flujo)
    cantidad_deseada = int(request.GET.get('cantidad', request.POST.get('cantidad', 1)))
    
    if request.method == 'POST':
        # 1. Capturar los datos del formulario de compra/agendamiento
        tipo_entrega = request.POST.get('tipo_entrega')  # 'retiro' o 'delivery'
        fecha_agendada = request.POST.get('fecha_agendada')
        tipo_pago = request.POST.get('tipo_pago')  # 'debito', 'credito', 'transferencia'
        
        # Datos opcionales si se seleccionó delivery
        nombre_receptor = request.POST.get('nombre_receptor', '')
        direccion_receptor = request.POST.get('direccion_receptor', '')
        telefono_receptor = request.POST.get('telefono_receptor', '')
        
        # 2. Calcular costos y totales multiplicados por la cantidad seleccionada (Si es delivery se suman los 3.000 CLP)
        costo_envio = 3000 if tipo_entrega == 'delivery' else 0
        total_pagado = (float(producto.precio_rescate) * cantidad_deseada) + costo_envio
        
        # 3. Crear el registro en AgendamientoLogistica usando 'cantidad'
        AgendamientoLogistica.objects.create(
            producto=producto,
            cliente_empresa=request.user.username,
            cantidad=cantidad_deseada,  # <--- CORREGIDO: Ahora coincide exactamente con el modelo
            repartidor_asignado='Flota B2B Express',
            fecha_recogida=fecha_agendada,
            tipo_entrega=tipo_entrega,
            tipo_pago=tipo_pago,
            costo_envio=costo_envio,
            total_pagado=total_pagado,
            nombre_receptor=nombre_receptor,
            direccion_receptor=direccion_receptor,
            telefono_receptor=telefono_receptor,
            estado_envio='Vendido / Agendado'
        )
        
        # 4. Gestionar el stock de forma parcial o total
        if cantidad_deseada >= producto.volumen_lote:
            producto.is_deleted = True
            producto.deleted_at = timezone.now()
            producto.volumen_lote = 0
        else:
            producto.volumen_lote -= cantidad_deseada
            
        producto.save()
        
        # 5. Redirigir a "Mis Compras"
        return redirect('movies:mis-compras')

    return render(request, 'movies/agendar_compra.html', {
        'producto': producto,
        'cantidad': cantidad_deseada
    })


# --- Placeholders y vistas conectadas a los paneles de logística/postventa ---
@login_required
def category_list(request):
    return render(request, 'movies/category/category_list.html')


@login_required
def panel_postventa(request):
    return render(request, 'movies/panel_postventa.html')


@login_required
def panel_ejecutivo_logistica(request):
    return render(request, 'movies/panel_ejecutivo_logistica.html')


@login_required
def coordinar_retiros(request):
    return render(request, 'movies/coordinar_retiros.html')


@login_required
def generar_etiqueta(request):
    return render(request, 'movies/generar_etiqueta.html')


@login_required
def panel_operador_logistica(request):
    return render(request, 'movies/panel_operador_logistica.html')


@login_required
def revisar_solicitudes(request):
    return render(request, 'movies/revisar_solicitudes.html')


@login_required
def validar_evidencia(request):
    return render(request, 'movies/validar_evidencia.html')


@login_required
def autorizar_devoluciones(request):
    return render(request, 'movies/autorizar_devoluciones.html')


@login_required
def aprobar_devolucion(request, pk):
    return redirect('movies:autorizar-devoluciones')


@login_required
def rechazar_devolucion(request, pk):
    return redirect('movies:autorizar-devoluciones')


@login_required
def ejecutar_retiros_envios(request):
    return render(request, 'movies/ejecutar_retiros_envios.html')


@login_required
def panel_administrador(request):
    productos = ProductoInverso.activos.all().prefetch_related('imagenes')
    return render(
        request, 'movies/panel_administrador.html', {'productos': productos}
    )


@login_required
def reportes_view(request):
    return render(request, 'movies/reportes.html')


@login_required
def panel_base_datos(request):
    return render(request, 'movies/panel_base_datos.html')


@login_required
def crear_solicitud(request):
    if request.method == 'POST':
        form = ProductoInversoForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.empresa = request.user
            prod.save()

            # --- PROCESAR MÚLTIPLES IMÁGENES ---
            files = request.FILES.getlist('imagenes')
            for index, f in enumerate(files):
                es_principal = index == 0  # La primera foto es la principal
                ImagenProducto.objects.create(
                    producto=prod, imagen=f, es_principal=es_principal
                )

            return redirect('movies:panel-cliente')
    else:
        form = ProductoInversoForm()
    return render(request, 'movies/crear_solicitud.html', {'form': form})


@login_required
def consultar_estado_solicitudes(request):
    return render(request, 'movies/consultar_estado_solicitudes.html')


@login_required
def coordinar_retiro_accion(request, solicitud_id):
    return redirect('movies:coordinar-retiros')


@login_required
def generar_etiqueta_accion(request, solicitud_id):
    return redirect('movies:generar-etiqueta')


@login_required
def ejecutar_retiros_envios_accion(request, solicitud_id):
    return redirect('movies:ejecutar-retiros-envios')


@login_required
def descargar_reporte(request):
    return redirect('movies:reportes')