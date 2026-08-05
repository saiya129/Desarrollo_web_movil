# Sistema de Logística Inversa — Devoluciones y Cambios

Plataforma web desarrollada en Django para la gestión del proceso de logística
inversa (devoluciones y cambios de productos) de un comercio electrónico.
Proyecto base tomado de [simple-crud-django](https://github.com/) (CRUD con
vistas basadas en funciones y autenticación) y adaptado al caso propuesto en
la Sumativa 1 (APTC106): digitalización del flujo de devoluciones entre
cliente, ejecutivo de postventa, ejecutivo de logística, operador de
logística y administrador.

## Roles y flujo del proceso

| Rol                    | Acciones principales                                                                                 |
|------------------------|------------------------------------------------------------------------------------------------------|
| Cliente                | Crea una solicitud de devolución/cambio adjuntando evidencia, consulta el estado de sus solicitudes. |
| Ejecutivo Postventa    | Revisa solicitudes, valida evidencia, aprueba o rechaza.                                             |
| Ejecutivo de Logística | Coordina el retiro y genera la etiqueta de reenvío de las solicitudes aprobadas.                     |
| Operador de Logística  | Ejecuta el retiro/envío una vez generada la etiqueta, cerrando la solicitud como completada.         |
| Administrador          | Accede a todos los paneles, visualiza indicadores (`reportes/`) y descarga el reporte en CSV.        |

El estado de una solicitud avanza así:
`Pendiente → Aprobada → Retiro Coordinado → Etiqueta Generada → Completado`
(o `Rechazada` si postventa la rechaza).

## Requisitos

- Python 3.12
- pip

## Instalación y ejecución local

```bash
# 1. Clonar/descomprimir el proyecto y ubicarse en la carpeta simple-crud-django-master
cd simple-crud-django-master

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requierements.txt

# 5. Aplicar migraciones
python manage.py migrate

# 6. (Opcional) crear un superusuario para acceder como administrador
python manage.py createsuperuser

# 7. Correr el servidor
python manage.py runserver
```

Luego abrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) e iniciar sesión.

> **Nota:** el rol de cada usuario se define en el modelo `UserProfile`
> (`postventa`, `ejecutivo_logistica`, `operador_logistica`, `administrador`).
> Un usuario sin `UserProfile` asociado es tratado como **cliente**. Los
> superusuarios (`is_superuser`) tienen acceso a todos los paneles sin
> importar su rol.

## Dependencias

```
Django==6.0.7
django-unfold==0.102.0
django-widget-tweaks==1.5.1
Pillow==12.3.0
```

## Estructura relevante

```
apps/movies/
├── models.py      # Movies/Categories (base original) + UserProfile y SolicitudDevolucion (dominio del proyecto)
├── views.py        # Vistas por rol y flujo de estados de la solicitud
├── forms.py
├── urls.py
└── templates/movies/  # Paneles por rol (panel_cliente, panel_postventa, panel_ejecutivo_logistica, etc.)
```

## Limitaciones conocidas / trabajo futuro

- Las vistas de transición de estado (`coordinar_retiro_accion`,
  `generar_etiqueta_accion`, `ejecutar_retiros_envios_accion`) no validan
  el estado previo de la solicitud, por lo que en la versión actual es
  posible saltarse pasos del flujo.
- No existe una operación de eliminación (Delete) para `SolicitudDevolucion`;
  el rechazo cumple un rol equivalente dentro del flujo de negocio.
- El MVP no incluye la aplicación móvil ni notificaciones en tiempo real
  descritas en la propuesta original; ambas quedan como trabajo futuro.