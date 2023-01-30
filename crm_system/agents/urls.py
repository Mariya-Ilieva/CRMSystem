from django.urls import path, include

from crm_system.agents.views import AgentListView, AgentCreateView, AgentDetailView, AgentUpdateView, AgentDeleteView

urlpatterns = [
    path('', AgentListView.as_view(), name='agents list'),
    path('create/', AgentCreateView.as_view(), name='agent create'),
    path('<int:pk>/', include([
        path('', AgentDetailView.as_view(), name='agent detail'),
        path('update/', AgentUpdateView.as_view(), name='agent update'),
        path('delete/', AgentDeleteView.as_view(), name='agent delete'),
    ]))
]
