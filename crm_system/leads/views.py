import logging
import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from crm_system.agents.mixins import OrganizerLoginRequiredMixin
from .models import Lead, Category, FollowUp
from .forms import LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm, \
    CategoryModelForm, FollowUpModelForm


logger = logging.getLogger(__name__)


class SignupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('login')


class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(OrganizerLoginRequiredMixin, generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        user = self.request.user
        total_lead_count = Lead.objects.filter(organisation=user.profile).count()
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        total_in_past30 = Lead.objects.filter(
            organisation=user.profile,
            date_added__gte=thirty_days_ago
        ).count()
        converted_category = Category.objects.get(name='Converted')
        converted_in_past30 = Lead.objects.filter(
            organisation=user.profile,
            category=converted_category,
            converted_date__gte=thirty_days_ago
        ).count()

        context.update({
            'total_lead_count': total_lead_count,
            'total_in_past30': total_in_past30,
            'converted_in_past30': converted_in_past30
        })
        return context


def landing_page(request):
    return render(request, 'landing.html')


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organisation=user.profile,
                agent__isnull=False
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
                agent__isnull=False
            )
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organisation=user.profile,
                agent__isnull=True
            )
            context.update({
                'unassigned_leads': queryset
            })
        return context


def lead_list(request):
    leads = Lead.objects.all()
    context = {
        'leads': leads
    }
    return render(request, 'leads/lead_list.html', context)


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organisation=user.profile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset


def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        'lead': lead
    }
    return render(request, 'leads/lead_detail.html', context)


class LeadCreateView(OrganizerLoginRequiredMixin, generic.CreateView):
    template_name = 'leads/lead_create.html'
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse('leads:lead-list')

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.profile
        lead.save()
        send_mail(
            subject='A lead has been created',
            message='Go to the site to see the new lead',
            from_email='test@test.com',
            recipient_list=['test2@test.com']
        )
        messages.success(self.request, 'You have successfully created a lead')
        return super(LeadCreateView, self).form_valid(form)


def lead_create(request):
    form = LeadModelForm()
    if request.method == 'POST':
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/leads')
    context = {
        'form': form
    }
    return render(request, 'leads/lead_create.html', context)


class LeadUpdateView(OrganizerLoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/lead_update.html'
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.profile)

    def get_success_url(self):
        return reverse('leads:lead-list')

    def form_valid(self, form):
        form.save()
        messages.info(self.request, 'You have successfully updated this lead')
        return super(LeadUpdateView, self).form_valid(form)


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == 'POST':
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('/leads')
    context = {
        'form': form,
        'lead': lead
    }
    return render(request, 'leads/lead_update.html', context)


class LeadDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/lead_delete.html'

    def get_success_url(self):
        return reverse('leads:lead-list')

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.profile)


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect('/leads')


class AssignAgentView(OrganizerLoginRequiredMixin, generic.FormView):
    template_name = 'leads/assign_agent.html'
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('leads:lead-list')

    def form_valid(self, form):
        agent = form.cleaned_data['agent']
        lead = Lead.objects.get(id=self.kwargs['pk'])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/category_list.html'
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organisation=user.profile
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
            )

        context.update({
            'unassigned_lead_count': queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(
                organisation=user.profile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/category_detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(
                organisation=user.profile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryCreateView(OrganizerLoginRequiredMixin, generic.CreateView):
    template_name = 'leads/category_create.html'
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse('leads:category-list')

    def form_valid(self, form):
        category = form.save(commit=False)
        category.organisation = self.request.user.profile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrganizerLoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/category_update.html'
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse('leads:category-list')

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(
                organisation=user.profile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/category_delete.html'

    def get_success_url(self):
        return reverse('leads:category-list')

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(
                organisation=user.profile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/lead_category_update.html'
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organisation=user.profile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse('leads:lead-detail', kwargs={'pk': self.get_object().id})

    def form_valid(self, form):
        lead_before_update = self.get_object()
        instance = form.save(commit=False)
        converted_category = Category.objects.get(name='Converted')
        if form.cleaned_data['category'] == converted_category:
            if lead_before_update.category != converted_category:
                instance.converted_date = datetime.datetime.now()
        instance.save()
        return super(LeadCategoryUpdateView, self).form_valid(form)


class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'leads/followup_create.html'
    form_class = FollowUpModelForm

    def get_success_url(self):
        return reverse('leads:lead-detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(FollowUpCreateView, self).get_context_data(**kwargs)
        context.update({
            'lead': Lead.objects.get(pk=self.kwargs['pk'])
        })
        return context

    def form_valid(self, form):
        lead = Lead.objects.get(pk=self.kwargs['pk'])
        followup = form.save(commit=False)
        followup.lead = lead
        followup.save()
        return super(FollowUpCreateView, self).form_valid(form)


class FollowUpUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/followup_update.html'
    form_class = FollowUpModelForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = FollowUp.objects.filter(lead__organisation=user.profile)
        else:
            queryset = FollowUp.objects.filter(lead__organisation=user.agent.organisation)
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse('leads:lead-detail', kwargs={'pk': self.get_object().lead.id})


class FollowUpDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/followup_delete.html'

    def get_success_url(self):
        followup = FollowUp.objects.get(id=self.kwargs['pk'])
        return reverse('leads:lead-detail', kwargs={'pk': followup.lead.pk})

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = FollowUp.objects.filter(lead__organisation=user.profile)
        else:
            queryset = FollowUp.objects.filter(lead__organisation=user.agent.organisation)
            queryset = queryset.filter(lead__agent__user=user)
        return queryset


class LeadJsonView(generic.View):
    def get(self, request, *args, **kwargs):
        qs = list(Lead.objects.all().values(
            'first_name',
            'last_name',
            'age')
        )
        return JsonResponse({
            'qs': qs,
        })
