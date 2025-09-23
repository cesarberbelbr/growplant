# cultivation/forms.py

from django import forms
from .models import Environment, Lighting, Plant, Stage
from datetime import date

class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        # Lista dos campos que o usuário poderá preencher no formulário
        fields = [
            'name',
            'height',
            'width',
            'depth',
            'lighting_system',
            'light_exposure_hours',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O Django por padrão já renderiza o ManyToManyField como um box de seleção múltipla,
        # mas podemos melhorar o widget se quisermos, como torná-lo um CheckboxSelectMultiple.
        self.fields['lighting_system'].widget = forms.CheckboxSelectMultiple()
        self.fields['lighting_system'].help_text = 'Selecione uma ou mais luzes para este ambiente.'
        self.fields['lighting_system'].required = False

class LightingForm(forms.ModelForm):
    class Meta:
        model = Lighting
        fields = ['light_type', 'watts']

class PlantForm(forms.ModelForm):
    # Definimos a data de germinação explicitamente para usar o widget de data do HTML5
    germination_date = forms.DateField(
        label="Data de Germinação",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today #
    )

    class Meta:
        model = Plant
        fields = [
            'name',
            'strain',
            'germination_date',
            'stage',
            'environment',
        ]

    def __init__(self, *args, **kwargs):
        # Pega o usuário que será passado pela view
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtra o campo 'environment' para mostrar apenas os ambientes do usuário logado
            self.fields['environment'].queryset = Environment.objects.filter(owner=user)
            # Adiciona o filtro para o campo de estágios
            self.fields['stage'].queryset = Stage.objects.filter(owner=user)

class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        # O 'owner' será definido na view
        fields = ['name', 'light_hours_on', 'duration', 'duration_unit']