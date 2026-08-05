from django.db import models
from django.contrib.auth.models import User

# --- Modelos Existentes del Proyecto ---
class Categories(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movies(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    # Agrega esta línea para asociar la película al usuario:
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')

    def __str__(self):
        return self.title


# --- Nuevo Modelo de Perfiles y Roles ---
class UserProfile(models.Model):
    POSTVENTA = 'postventa'
    EJECUTIVO_LOGISTICA = 'ejecutivo_logistica'
    OPERADOR_LOGISTICA = 'operador_logistica'
    ADMINISTRADOR = 'administrador'

    ROLE_CHOICES = [
        (POSTVENTA, 'Ejecutivo Postventa'),
        (EJECUTIVO_LOGISTICA, 'Ejecutivo de Logística'),
        (OPERADOR_LOGISTICA, 'Operador de Logística'),
        (ADMINISTRADOR, 'Administrador'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='Usuario'
    )
    role = models.CharField(
        max_length=30, 
        choices=ROLE_CHOICES, 
        default=POSTVENTA,
        verbose_name='Rol en la Plataforma'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    # --- Modelo para Solicitudes de Devolución del Cliente ---
class SolicitudDevolucion(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    producto = models.CharField(max_length=200, verbose_name='Nombre o Código del Producto')
    motivo = models.TextField(verbose_name='Motivo de la devolución')
    evidencia = models.ImageField(upload_to='evidencias/', verbose_name='Evidencia del producto')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente', verbose_name='Estado de la solicitud')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')

    def __str__(self):
        return f"Solicitud de {self.usuario.username} - {self.producto}"