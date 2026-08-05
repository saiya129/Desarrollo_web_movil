from django.contrib import admin
from unfold.admin import ModelAdmin  # 1. Importa esto desde unfold
from .models import UserProfile, Categories, Movies  # (O los modelos que tengas)

# 2. Registra tus modelos heredando de ModelAdmin en lugar de admin.ModelAdmin
@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

@admin.register(Categories)
class CategoriessAdmin(ModelAdmin):
    list_display = ('name',) # Ajusta según los campos de tu modelo

@admin.register(Movies)
class MoviessAdmin(ModelAdmin):
    list_display = ('title',) # Ajusta según los campos de tu modelo