import random

from django.core.mail import send_mail
from django.views import generic
from django.shortcuts import reverse

from crm_system.agents.models import Agent
from crm_system.agents.forms import AgentModelForm
from crm_system.agents.mixins import OrganizerLoginRequiredMixin


class AgentListView(OrganizerLoginRequiredMixin, generic.ListView):
    template_name = 'agents/agent_list.html'

    def get_queryset(self):
        organisation = self.request.user.profile
        return Agent.objects.filter(organisation=organisation)


class AgentCreateView(OrganizerLoginRequiredMixin, generic.CreateView):
    template_name = 'agents/agent_create.html'
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse('agents:agent-list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organizer = False
        user.set_password(f'{random.randint(0, 1000000)}')
        user.save()
        Agent.objects.create(
            user=user,
            organisation=self.request.user.profile
        )
        send_mail(
            subject="You are invited to be an agent",
            message="You were added as an agent on CRM. Please come login to start working.",
            from_email="admin@test.com",
            recipient_list=[user.email]
        )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrganizerLoginRequiredMixin, generic.DetailView):
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        organisation = self.request.user.profile
        return Agent.objects.filter(organisation=organisation)


class AgentUpdateView(OrganizerLoginRequiredMixin, generic.UpdateView):
    template_name = 'agents/agent_update.html'
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse('agents:agent-list')

    def get_queryset(self):
        organisation = self.request.user.profile
        return Agent.objects.filter(organisation=organisation)


class AgentDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent_delete.html'
    context_object_name = 'agent'

    def get_success_url(self):
        return reverse('agents:agent-list')

    def get_queryset(self):
        organisation = self.request.user.profile
        return Agent.objects.filter(organisation=organisation)
