from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin

from .models import Environment, Lighting, Plant
from .forms import EnvironmentForm, LightingForm, PlantForm


# --- Views para Environments (Ambientes) ---

class EnvironmentListView(LoginRequiredMixin, ListView):
    model = Environment
    template_name = 'cultivation/environment_list.html'
    context_object_name = 'environments'

    def get_queryset(self):
        # Filtra os ambientes para mostrar apenas os do usuário logado
        return Environment.objects.filter(owner=self.request.user)


class EnvironmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Environment
    template_name = 'cultivation/environment_detail.html'

    def test_func(self):
        # Garante que o usuário só pode ver detalhes dos seus próprios ambientes
        environment = self.get_object()
        return self.request.user == environment.owner


class EnvironmentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Environment
    form_class = EnvironmentForm
    template_name = 'cultivation/environment_form.html'
    success_url = reverse_lazy('cultivation:environment_list')
    success_message = "Ambiente '%(name)s' criado com sucesso!"

    def form_valid(self, form):
        # Define o 'owner' do ambiente como o usuário logado antes de salvar
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print("\n\n[DEBUG] Formulário de Criação INVÁLIDO. Erros:")
        print(form.errors.as_data())
        print("[FIM DO DEBUG]\n")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Adicionar Novo Ambiente'
        return context


class EnvironmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Environment
    form_class = EnvironmentForm
    template_name = 'cultivation/environment_form.html'
    success_url = reverse_lazy('cultivation:environment_list')
    success_message = "Ambiente '%(name)s' atualizado com sucesso!"

    def test_func(self):
        environment = self.get_object()
        return self.request.user == environment.owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Ambiente'
        return context


class EnvironmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Environment
    template_name = 'cultivation/environment_confirm_delete.html'
    success_url = reverse_lazy('cultivation:environment_list')
    success_message = "Ambiente excluído com sucesso!"

    def test_func(self):
        environment = self.get_object()
        return self.request.user == environment.owner


# --- View para Lighting (Fontes de Luz) ---

class LightingListView(LoginRequiredMixin, ListView):
    model = Lighting
    template_name = 'cultivation/lighting_list.html'
    context_object_name = 'lights'

class LightingListView(LoginRequiredMixin, ListView):
    model = Lighting
    template_name = 'cultivation/lighting_list.html'
    context_object_name = 'lights'

class LightingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Lighting
    form_class = LightingForm
    template_name = 'cultivation/lighting_form.html'
    success_url = reverse_lazy('cultivation:lighting_list')
    success_message = "Fonte de luz criada com sucesso!"

class LightingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Lighting
    form_class = LightingForm
    template_name = 'cultivation/lighting_form.html'
    success_url = reverse_lazy('cultivation:lighting_list')
    success_message = "Fonte de luz atualizada com sucesso!"

class LightingDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Lighting
    template_name = 'cultivation/lighting_confirm_delete.html'
    success_url = reverse_lazy('cultivation:lighting_list')
    success_message = "Fonte de luz excluída com sucesso!"


class PlantListView(LoginRequiredMixin, ListView):
    model = Plant
    template_name = 'cultivation/plant_list.html'
    context_object_name = 'plants'

    def get_queryset(self):
        # Busca todas as plantas do usuário de uma só vez, otimizando a consulta
        return Plant.objects.filter(owner=self.request.user).select_related('environment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_plants = context['plants']

        # --- LÓGICA DE AGRUPAMENTO ATUALIZADA ---

        # Dicionário para plantas COM ambiente
        plants_by_environment = {}
        # Lista para plantas SEM ambiente
        plants_without_environment = []

        for plant in all_plants:
            if plant.environment:
                # Se o ambiente desta planta ainda não é uma chave no dicionário,
                # crie a chave com uma lista vazia.
                if plant.environment not in plants_by_environment:
                    plants_by_environment[plant.environment] = []

                # Adiciona a planta à lista do seu ambiente.
                plants_by_environment[plant.environment].append(plant)
            else:
                plants_without_environment.append(plant)

        # A lógica acima automaticamente garante que apenas ambientes
        # que têm pelo menos uma planta se tornarão chaves no dicionário.
        # Ambientes vazios nunca serão adicionados.

        # --- FIM DA LÓGICA ---

        context['plants_by_environment'] = plants_by_environment
        context['plants_without_environment'] = plants_without_environment

        return context


class PlantDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Plant
    template_name = 'cultivation/plant_detail.html'

    def test_func(self):
        plant = self.get_object()
        return self.request.user == plant.owner


class PlantCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Plant
    form_class = PlantForm
    template_name = 'cultivation/plant_form.html'
    success_url = reverse_lazy('cultivation:plant_list')
    success_message = "Planta '%(name)s - %(strain)s' cadastrada com sucesso!"

    def get_form_kwargs(self):
        # Passa o usuário logado para o __init__ do formulário
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Adicionar Nova Planta'
        return context


class PlantUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Plant
    form_class = PlantForm
    template_name = 'cultivation/plant_form.html'
    success_url = reverse_lazy('cultivation:plant_list')
    success_message = "Planta '%(name)s - %(strain)s' atualizada com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        plant = self.get_object()
        return self.request.user == plant.owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Planta'
        return context


class PlantDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Plant
    template_name = 'cultivation/plant_confirm_delete.html'
    success_url = reverse_lazy('cultivation:plant_list')
    success_message = "Planta excluída com sucesso!"

    def test_func(self):
        plant = self.get_object()
        return self.request.user == plant.owner