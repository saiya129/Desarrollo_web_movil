# Sistema de Logística Inversa

Plataforma web desarrollada en Django para la publicación, adquisición y gestión logística de productos provenientes de procesos de logística inversa.

Proyecto base tomado de [simple-crud-django](https://github.com/) (CRUD con vistas basadas en funciones y autenticación) y adaptado al caso de logística inversa desarrollado por el equipo en la Sumativa 2 (APTC106), incorporando funcionalidades de publicación de lotes, Marketplace, adquisición y gestión logística.

## Roles y flujo del proceso

| Rol                         | Acciones principales                                                                 |
|----------------------------|--------------------------------------------------------------------------------------|
| Cliente / Comprador B2B    | Consulta productos disponibles, realiza adquisiciones y revisa sus compras y seguimiento. |
| Empresa / Proveedor        | Publica y administra lotes de productos y revisa las operaciones asociadas a sus publicaciones. |

El flujo principal de la aplicación considera:

`Publicación de lote → Marketplace → Adquisición → Gestión logística → Seguimiento`

La adquisición puede realizarse mediante retiro en bodega o mediante delivery, dependiendo de la opción seleccionada por el usuario.

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

> **Nota:** > el tipo de usuario se define mediante el modelo `PerfilUsuario`.
> Los tipos contemplados son **cliente** y **empresa**.

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
├── migrations/ # Migraciones de la base de datos
├── templates/ # Plantillas HTML del aplicativo
├── admin.py # Configuración del panel de administración
├── apps.py # Configuración de la aplicación
├── forms.py # Formularios del aplicativo
├── models.py # Modelos de productos, perfiles y agendamiento logístico
├── tests.py # Pruebas de la aplicación
├── urls.py # Rutas del aplicativo
└── views.py # Vistas del Marketplace, productos, adquisiciones y logística
```