# cultivation/urls.py

from django.urls import path
from . import views

app_name = 'cultivation'

urlpatterns = [
    # READ: Lista de todos os ambientes
    path('', views.EnvironmentListView.as_view(), name='environment_list'),
    # READ: Detalhes de um ambiente específico
    path('<int:pk>/', views.EnvironmentDetailView.as_view(), name='environment_detail'),
    # CREATE: Página para criar um novo ambiente
    path('add/', views.EnvironmentCreateView.as_view(), name='environment_add'),
    # UPDATE: Página para editar um ambiente existente
    path('<int:pk>/edit/', views.EnvironmentUpdateView.as_view(), name='environment_edit'),
    # DELETE: Página para confirmar a exclusão de um ambiente
    path('<int:pk>/delete/', views.EnvironmentDeleteView.as_view(), name='environment_delete'),

    # Lista de Fontes de Luz disponíveis (catálogo)
    path('lighting/', views.LightingListView.as_view(), name='lighting_list'),
    # CREATE: Página para adicionar uma nova luz
    path('lighting/add/', views.LightingCreateView.as_view(), name='lighting_add'),
    # UPDATE: Página para editar uma luz
    path('lighting/<int:pk>/edit/', views.LightingUpdateView.as_view(), name='lighting_edit'),
    # DELETE: Página para confirmar a exclusão
    path('lighting/<int:pk>/delete/', views.LightingDeleteView.as_view(), name='lighting_delete'),

    # --- NOVAS URLs PARA PLANT (PLANTAS) ---
    path('plants/', views.PlantListView.as_view(), name='plant_list'),
    path('plants/<int:pk>/', views.PlantDetailView.as_view(), name='plant_detail'),
    path('plants/add/', views.PlantCreateView.as_view(), name='plant_add'),
    path('plants/<int:pk>/edit/', views.PlantUpdateView.as_view(), name='plant_edit'),
    path('plants/<int:pk>/delete/', views.PlantDeleteView.as_view(), name='plant_delete'),

    # --- NOVAS URLs PARA STAGE (ESTÁGIOS) ---
    path('stages/', views.StageListView.as_view(), name='stage_list'),
    path('stages/add/', views.StageCreateView.as_view(), name='stage_add'),
    path('stages/<int:pk>/edit/', views.StageUpdateView.as_view(), name='stage_edit'),
    path('stages/<int:pk>/delete/', views.StageDeleteView.as_view(), name='stage_delete'),

]