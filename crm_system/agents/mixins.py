from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class OrganizerLoginRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated and is an organizer."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_organizer:
            return redirect('leads:lead-list')
        return super().dispatch(request, *args, **kwargs)
