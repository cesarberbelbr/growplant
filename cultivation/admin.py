from django.contrib import admin
from .models import Environment, Lighting, Plant


@admin.register(Lighting)
class LightingAdmin(admin.ModelAdmin):
    # O campo 'name' foi removido do list_display e do search_fields
    list_display = ('__str__', 'light_type', 'watts')
    list_filter = ('light_type',)
    search_fields = ('watts',)  # Agora só podemos pesquisar por potência

    # Exibe '__str__' para que o nome calculado ("LED - 100W") seja a primeira coluna.
    def display_str(self, obj):
        return str(obj)

    display_str.short_description = "Identificador da Luz"

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'get_dimensions', 'light_exposure_hours', 'is_active')
    list_filter = ('owner', 'is_active')
    search_fields = ('name', 'owner__email')
    filter_horizontal = ('lighting_system',)

    @admin.display(description="Dimensões (A x L x P cm)")
    def get_dimensions(self, obj):
        return f"{obj.height} x {obj.width} x {obj.depth}"

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'strain', 'owner', 'environment', 'stage', 'germination_date', 'is_active')
    list_filter = ('stage', 'is_active', 'owner', 'environment')
    search_fields = ('name', 'strain', 'owner__email')

    def get_queryset(self, request):
        # Otimiza a consulta para evitar múltiplas buscas ao banco de dados
        return super().get_queryset(request).select_related('owner', 'environment')