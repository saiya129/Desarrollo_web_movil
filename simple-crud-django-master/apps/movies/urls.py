
from django.urls import path, re_path, include
from apps.movies import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'movies'

movies_patterns = [
    re_path(r'^inicio/$', views.movie_list, name='home'),
    re_path(r'^(?P<pk>[0-9]+)/$', views.movie_detail, name='movies-detail'),
    re_path(r'^crear/$', views.movie_create, name='movies-create'),
    re_path(r'^(?P<pk>[0-9]+)/editar/$', views.movie_update, name='movies-edit'),
    re_path(r'^(?P<pk>[0-9]+)/eliminar/$', views.movie_delete, name='movies-delete')
]

urlpatterns = [
    re_path(r'^$', views.log_in, name='log-in'),
    re_path(r'^log-out/$', views.log_out, name='log-out'),
    re_path(r'^categorias/$', views.category_list, name='category-list'),
    
    # Rutas para los paneles específicos por rol:
    re_path(r'^postventa/panel/$', views.panel_postventa, name='panel-postventa'),
    re_path(r'^logistica/ejecutivo/$', views.panel_ejecutivo_logistica, name='panel-ejecutivo-logistica'),
    re_path(r'^logistica/ejecutivo/retiros/$', views.coordinar_retiros, name='coordinar_retiros'),
    re_path(r'^logistica/ejecutivo/etiquetas/$', views.generar_etiqueta, name='generar_etiqueta'),
    re_path(r'^logistica/operador/$', views.panel_operador_logistica, name='panel-operador-logistica'),
    # Rutas para el panel de postventa y sus funciones:
    re_path(r'^postventa/panel/$', views.panel_postventa, name='panel-postventa'),
    re_path(r'^postventa/solicitudes/$', views.revisar_solicitudes, name='revisar_solicitudes'),
    re_path(r'^postventa/evidencia/$', views.validar_evidencia, name='validar_evidencia'),
    re_path(r'^postventa/devoluciones/$', views.autorizar_devoluciones, name='autorizar_devoluciones'),
    re_path(r'^postventa/devoluciones/aprobar/(?P<pk>[0-9]+)/$', views.aprobar_devolucion, name='aprobar-devolucion'),
    re_path(r'^postventa/devoluciones/rechazar/(?P<pk>[0-9]+)/$', views.rechazar_devolucion, name='rechazar-devolucion'),
    re_path(r'^operador/ejecutar/$', views.ejecutar_retiros_envios, name='ejecutar_retiros_envios'),
    re_path(r'^administrador/panel/$', views.panel_administrador, name='panel-administrador'),
    re_path(r'^reportes/$', views.reportes_view, name='reportes'),
    re_path(r'^administrador/base-datos/$', views.panel_base_datos, name='panel-base-datos'),
    re_path(r'^solicitud/nueva/$', views.crear_solicitud, name='crear_solicitud'),
    re_path(r'^solicitudes/estado/$', views.consultar_estado_solicitudes, name='consultar_estado_solicitudes'),
    re_path(r'^cliente/panel/$', views.panel_cliente, name='panel-cliente'),
    re_path(r'^logistica/coordinar/(?P<solicitud_id>\d+)/$', views.coordinar_retiro_accion, name='coordinar_retiro_accion'),
    re_path(r'^logistica/generar-etiqueta-accion/(?P<solicitud_id>\d+)/$', views.generar_etiqueta_accion, name='generar_etiqueta_accion'),
    re_path(r'^logistica/ejecutar-accion/(?P<solicitud_id>\d+)/$', views.ejecutar_retiros_envios_accion, name='ejecutar_retiros_envios_accion'),
    re_path(r'^administrador/reportes/descargar/$', views.descargar_reporte, name='descargar-reporte'),
    
    re_path(r'^peliculas/', include(movies_patterns))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)