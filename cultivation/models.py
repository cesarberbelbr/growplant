import datetime

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import decimal

class Lighting(models.Model):
    """
    Representa uma fonte de luz que pode ser usada em um ambiente.
    Agora identificada pelo tipo e pela potência.
    """
    class LightTypes(models.TextChoices):
        LED = 'LED', _('LED') # Simplificado para melhor exibição
        HPS = 'HPS', _('HPS')
        MH = 'MH', _('MH')
        CMH = 'CMH', _('CMH')
        FLUORESCENT = 'FLR', _('Fluorescente')
        OTHER = 'OTH', _('Outro')

    light_type = models.CharField(
        max_length=3,
        choices=LightTypes.choices,
        default=LightTypes.LED,
        verbose_name=_("Tipo de Luz")
    )
    watts = models.PositiveIntegerField(verbose_name=_("Potência (Watts)"))

    def __str__(self):
        # O __str__ agora é uma combinação do tipo e da potência
        return f"{self.get_light_type_display()} - {self.watts}W"

    class Meta:
        verbose_name = _("Fonte de Luz")
        verbose_name_plural = _("Fontes de Luz")
        # Adiciona uma restrição para garantir que a combinação de tipo e potência seja única.
        # Isso impede o cadastro de duas luzes "LED - 100W", por exemplo.
        unique_together = ('light_type', 'watts')
        ordering = ['light_type', 'watts'] # Ordena a lista


class Environment(models.Model):
    """
    Representa um ambiente de cultivo, como uma estufa.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='environments',
        verbose_name=_("Proprietário")
    )
    name = models.CharField(
        max_length=100,
        default="Estufa",
        verbose_name=_("Nome do Ambiente")
    )
    # Dimensões em centímetros
    height = models.DecimalField(
        verbose_name=_("Altura (cm)"),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal('0.01'))]
    )
    width = models.DecimalField(
        verbose_name=_("Largura (cm)"),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal('0.01'))]
    )
    depth = models.DecimalField(
        verbose_name=_("Profundidade (cm)"),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal('0.01'))]
    )
    # Relação "Muitos para Muitos"
    lighting_system = models.ManyToManyField(
        Lighting,
        verbose_name=_("Sistema de Iluminação"),
        blank=True,
    )
    # Tempo de exposição à luz (horas/dia)
    light_exposure_hours = models.PositiveSmallIntegerField(
        default=12,
        verbose_name=_("Tempo de Exposição à Luz (horas/dia)"),
        help_text=_("Número de horas que as luzes ficam acesas por dia.")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Ambiente de Cultivo")
        verbose_name_plural = _("Ambientes de Cultivo")

class Stage(models.Model):
    """
    Representa um estágio de cultivo customizável pelo usuário.
    """
    class DurationUnit(models.TextChoices):
        DAYS = 'D', _('Dias')
        WEEKS = 'W', _('Semanas')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    name = models.CharField(max_length=100, verbose_name=_("Nome do Estágio"))
    light_hours_on = models.PositiveSmallIntegerField(
        default=12,
        verbose_name=_("Horas de Luz (Ligada)"),
        help_text=_("Número de horas que as luzes ficam LIGADAS por dia neste estágio.")
    )
    duration = models.PositiveIntegerField(
        verbose_name=_("Duração Estimada")
    )
    duration_unit = models.CharField(
        max_length=1,
        choices=DurationUnit.choices,
        default=DurationUnit.WEEKS,
        verbose_name=_("Unidade de Duração")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Estágio de Cultivo")
        verbose_name_plural = _("Estágios de Cultivo")
        # Garante que um usuário não pode ter dois estágios com o mesmo nome
        unique_together = ('owner', 'name')

class Plant(models.Model):
    """
    Representa uma única planta sendo cultivada.
    """
    class PlantStage(models.TextChoices):
        GERMINATION = 'GERM', _('Germinação')
        SEEDLING = 'SEED', _('Plântula')
        VEGETATIVE = 'VEGE', _('Vegetativo')
        FLOWERING = 'FLOW', _('Floração')
        HARVESTED = 'HARV', _('Colhida')
        OTHER = 'OTHR', _('Outro')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='plants',
        verbose_name=_("Proprietário")
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.SET_NULL, # Se o ambiente for deletado, não delete a planta
        null=True,                 # Permite que a planta exista sem estar em um ambiente
        blank=True,                # Opcional nos formulários
        related_name='plants',
        verbose_name=_("Ambiente de Cultivo")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nome da Planta"),
        default="Planta",
        help_text=_("Um nome ou identificador para esta planta específica. Ex: Skunk #1")
    )
    strain = models.CharField(
        max_length=100,
        verbose_name=_("Genética / Variedade"),
        default="Variedade Desconhecida",
        help_text=_("O nome da variedade ou 'strain'. Ex: White Widow, Tomate Cereja")
    )
    germination_date = models.DateField(verbose_name=_("Data de Germinação"), default=datetime.date.today)
    stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL, # Se o estágio for deletado, não delete a planta
        null=True,                 # Permite nulo
        blank=True,                # Opcional no formulário
        verbose_name=_("Estágio Atual")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Ativa"),
        help_text=_("Desmarque se a planta foi descartada ou não está mais sendo monitorada.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.strain})"

    @property
    def age_in_days(self):
        """Calcula a idade da planta em dias desde a germinação."""
        from datetime import date
        today = date.today()
        age = today - self.germination_date
        return age.days

    @property
    def age_in_weeks(self):
        """Calcula a idade da planta em semanas e dias."""
        days_old = self.age_in_days

        if days_old < 0:
            return "Ainda não germinou"

        weeks = days_old // 7  # Divisão inteira para obter o número de semanas completas
        days = days_old % 7  # O resto da divisão para obter os dias restantes

        if weeks > 0 and days > 0:
            return f"{weeks} semana(s) e {days} dia(s)"
        elif weeks > 0:
            return f"{weeks} semana(s)"
        else:
            return f"{days} dia(s)"

    class Meta:
        verbose_name = _("Planta")
        verbose_name_plural = _("Plantas")
        ordering = ['-germination_date', 'name']