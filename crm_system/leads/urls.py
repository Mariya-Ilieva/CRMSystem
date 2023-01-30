from django.urls import path, include
from .views import LeadListView, LeadDetailView, LeadCreateView, LeadUpdateView, LeadDeleteView, AssignAgentView, \
    CategoryListView, CategoryDetailView, LeadCategoryUpdateView, CategoryCreateView, CategoryUpdateView, \
    CategoryDeleteView, LeadJsonView, FollowUpCreateView, FollowUpUpdateView, FollowUpDeleteView

urlpatterns = [
    path('', LeadListView.as_view(), name='lead list'),
    path('json/', LeadJsonView.as_view(), name='lead list json'),
    path('<int:pk>/', include([
        path('', LeadDetailView.as_view(), name='lead detail'),
        path('update/', LeadUpdateView.as_view(), name='lead update'),
        path('delete/', LeadDeleteView.as_view(), name='lead delete'),
        path('assign-agent/', AssignAgentView.as_view(), name='assign agent'),
        path('category/', LeadCategoryUpdateView.as_view(), name='lead category update'),
        path('followups/create/', FollowUpCreateView.as_view(), name='lead followup create'),
        ])),
    path('followups/<int:pk>/', FollowUpUpdateView.as_view(), name='lead followup update'),
    path('followups/<int:pk>/delete/', FollowUpDeleteView.as_view(), name='lead followup delete'),
    path('create/', LeadCreateView.as_view(), name='lead create'),
    path('categories/', include([
        path('', CategoryListView.as_view(), name='category list'),
        path('<int:pk>/', CategoryDetailView.as_view(), name='category detail'),
        path('<int:pk>/update/', CategoryUpdateView.as_view(), name='category update'),
        path('<int:pk>/delete/', CategoryDeleteView.as_view(), name='category delete'),
        ])),
    path('create-category/', CategoryCreateView.as_view(), name='category create'),
]
