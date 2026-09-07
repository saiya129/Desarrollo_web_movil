from django.contrib import admin
from .models import AgendamientoLogistica, PerfilUsuario, ProductoInverso

# Registramos los nuevos modelos limpios
admin.site.register(PerfilUsuario)
admin.site.register(ProductoInverso)
admin.site.register(AgendamientoLogistica)
