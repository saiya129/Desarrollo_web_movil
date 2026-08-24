from decimal import Decimal
from django import forms
from .models import ProductoInverso


class ProductoInversoForm(forms.ModelForm):

    class Meta:
        model = ProductoInverso
        fields = [
            'titulo',
            'descripcion',
            'categoria',             # <--- ¡Añadido aquí!
            'codigo_ean',
            'volumen_lote',
            'marca',
            'tienda_origen',
            'ubicacion',
            'precio_original',
            'precio_rescate',
            'estado_fisico',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}), # <--- ¡Añadido con su widget de selección!
            'codigo_ean': forms.TextInput(attrs={'class': 'form-control'}),
            'volumen_lote': forms.NumberInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'tienda_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_original': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_rescate': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_fisico': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_codigo_ean(self):
        ean = self.cleaned_data.get('codigo_ean')
        if not ean.isdigit() or len(ean) != 13:
            raise forms.ValidationError(
                'El código EAN debe ser estrictamente numérico y contener 13 dígitos.'
            )
        return ean

    def clean_precio_original(self):
        precio = self.cleaned_data.get('precio_original')
        if precio is not None:
            # Redondea limpiamente a 2 decimales para evitar fracciones raras
            return round(Decimal(str(precio)), 2)
        return precio

    def clean_precio_rescate(self):
        precio = self.cleaned_data.get('precio_rescate')
        if precio is not None:
            # Redondea limpiamente a 2 decimales para evitar fracciones raras
            return round(Decimal(str(precio)), 2)
        return precio