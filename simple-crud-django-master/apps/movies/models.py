from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ProductoInversoManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ProductoInverso(models.Model):
    # Opciones de categorías para mantener consistencia
    CATEGORIA_CHOICES = [
        ('ropa', 'Ropa'),
        ('electrodomesticos', 'Electrodomésticos'),
        ('tecnologia', 'Tecnología'),
    ]

    # Relaciones y datos básicos
    empresa = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='productos_inversos'
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    codigo_ean = models.CharField(max_length=13)
    volumen_lote = models.PositiveIntegerField(default=1)
    
    # Campo de categoría sin default forzado para que el usuario elija
    categoria = models.CharField(
        max_length=50, choices=CATEGORIA_CHOICES
    )

    # Atributos comerciales y logísticos
    marca = models.CharField(max_length=100, blank=True, null=True)
    tienda_origen = models.CharField(max_length=100, blank=True, null=True)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2)
    precio_rescate = models.DecimalField(max_digits=10, decimal_places=2)
    estado_fisico = models.CharField(max_length=100)

    # Control de borrado lógico
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    # Managers
    objects = models.Manager()  # Manager por defecto
    activos = ProductoInversoManager()  # Manager para solo activos

    def __str__(self):
        return f'{self.titulo} - {self.empresa.username}'


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        ProductoInverso, related_name='imagenes', on_delete=models.CASCADE
    )
    imagen = models.ImageField(upload_to='productos_inversos/')
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f'Imagen para {self.producto.titulo} (Principal: {self.es_principal})'


class PerfilUsuario(models.Model):
    TIPO_CHOICES = (
        ('cliente', 'Cliente / Comprador B2B'),
        ('empresa', 'Empresa / Proveedor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='cliente'
    )

    def __str__(self):
        return f'{self.user.username} - {self.tipo}'


class AgendamientoLogistica(models.Model):
    producto = models.ForeignKey(ProductoInverso, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)  # <--- Campo agregado para guardar las unidades adquiridas
    repartidor_asignado = models.CharField(
        max_length=150, default='Flota B2B Express'
    )
    cliente_empresa = models.CharField(max_length=150)
    
    # Modificado a DateTimeField para aceptar fecha y hora del formulario
    fecha_recogida = models.DateTimeField()
    
    franja_horaria = models.CharField(max_length=100, blank=True, null=True)
    estado_envio = models.CharField(
        max_length=100, default='Agendado / Pendiente de retiro'
    )
    fecha_agendamiento = models.DateTimeField(default=timezone.now)
    
    tipo_entrega = models.CharField(max_length=50, default='retiro')
    tipo_pago = models.CharField(max_length=50, default='debito')
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nombre_receptor = models.CharField(max_length=150, blank=True, null=True)
    direccion_receptor = models.CharField(max_length=250, blank=True, null=True)
    telefono_receptor = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'Retiro para {self.producto.titulo} ({self.cantidad} un.) - {self.estado_envio}'
