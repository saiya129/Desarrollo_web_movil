from apps.movies import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

app_name = 'movies'

urlpatterns = [
    re_path(r'^$', views.log_in, name='log-in'),
    re_path(r'^log-out/$', views.log_out, name='log-out'),
    re_path(r'^categorias/$', views.category_list, name='category-list'),
    
    # --- Nuevas Rutas para Marketplace, Pestañas y Logística Inversa ---
    re_path(r'^cliente/panel/$', views.panel_cliente, name='panel-cliente'),
    re_path(r'^mis-productos/$', views.mis_productos, name='mis-productos'),
    re_path(r'^mis-compras/$', views.mis_compras, name='mis-compras'),
    re_path(r'^producto/(?P<pk>[0-9]+)/$', views.detalle_producto, name='detalle-producto'),
    re_path(r'^producto/(?P<pk>[0-9]+)/editar/$', views.editar_producto, name='editar-producto'),
    re_path(r'^producto/(?P<pk>[0-9]+)/agendar/$', views.agendar_retiro_producto, name='agendar-retiro-producto'),
    re_path(r'^producto/(?P<pk>[0-9]+)/eliminar/$', views.soft_delete_producto, name='soft-delete-producto'),
    
    # Ruta de Seguimiento de Compra
    re_path(r'^compra/(?P<pk>[0-9]+)/seguimiento/$', views.seguimiento_compra, name='seguimiento-compra'),
    
    # Rutas para los paneles específicos por rol:
    re_path(r'^postventa/panel/$', views.panel_postventa, name='panel-postventa'),
    re_path(
        r'^logistica/ejecutivo/$',
        views.panel_ejecutivo_logistica,
        name='panel-ejecutivo-logistica',
    ),
    re_path(
        r'^logistica/ejecutivo/retiros/$',
        views.coordinar_retiros,
        name='coordinar-retiros',
    ),
    re_path(
        r'^logistica/ejecutivo/etiquetas/$',
        views.generar_etiqueta,
        name='generar-etiqueta',
    ),
    re_path(
        r'^logistica/operador/$',
        views.panel_operador_logistica,
        name='panel-operador-logistica',
    ),
    # Rutas para el panel de postventa y sus funciones:
    re_path(r'^postventa/panel/$', views.panel_postventa, name='panel-postventa'),
    re_path(
        r'^postventa/solicitudes/$',
        views.revisar_solicitudes,
        name='revisar-solicitudes',
    ),
    re_path(
        r'^postventa/evidencia/$',
        views.validar_evidencia,
        name='validar-evidencia',
    ),
    re_path(
        r'^postventa/devoluciones/$',
        views.autorizar_devoluciones,
        name='autorizar-devoluciones',
    ),
    re_path(
        r'^postventa/devoluciones/aprobar/(?P<pk>[0-9]+)/$',
        views.aprobar_devolucion,
        name='aprobar-devolucion',
    ),
    re_path(
        r'^postventa/devoluciones/rechazar/(?P<pk>[0-9]+)/$',
        views.rechazar_devolucion,
        name='rechazar-devolucion',
    ),
    re_path(
        r'^operador/ejecutar/$',
        views.ejecutar_retiros_envios,
        name='ejecutar-retiros-envios',
    ),
    re_path(
        r'^administrador/panel/$',
        views.panel_administrador,
        name='panel-administrador',
    ),
    re_path(r'^reportes/$', views.reportes_view, name='reportes'),
    re_path(
        r'^administrador/base-datos/$',
        views.panel_base_datos,
        name='panel-base-datos',
    ),
    re_path(r'^solicitud/nueva/$', views.crear_solicitud, name='crear-solicitud'),
    re_path(
        r'^solicitudes/estado/$',
        views.consultar_estado_solicitudes,
        name='consultar_estado_solicitudes',
    ),
    re_path(
        r'^logistica/coordinar/(?P<solicitud_id>\d+)/$',
        views.coordinar_retiro_accion,
        name='coordinar_retiro_accion',
    ),
    re_path(
        r'^logistica/generar-etiqueta-accion/(?P<solicitud_id>\d+)/$',
        views.generar_etiqueta_accion,
        name='generar_etiqueta_accion',
    ),
    re_path(
        r'^logistica/ejecutar-accion/(?P<solicitud_id>\d+)/$',
        views.ejecutar_retiros_envios_accion,
        name='ejecutar_retiros_envios_accion',
    ),
    re_path(
        r'^administrador/reportes/descargar/$',
        views.descargar_reporte,
        name='descargar-reporte',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)