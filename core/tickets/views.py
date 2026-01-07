from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Ticket


class TicketListView(ListView):
    model = Ticket
    template_name = "tickets/ticket_list.html"
    ordering = ["is_completed", "-date"]


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = ["title", "body", "is_completed"]
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("ticket_list")
    login_url = reverse_lazy("login")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class OwnerOrSuperuserQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(author=user)


class TicketUpdateView(
        LoginRequiredMixin, OwnerOrSuperuserQuerysetMixin, UpdateView):
    model = Ticket
    fields = ["title", "body", "is_completed"]
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("ticket_list")
    login_url = reverse_lazy("login")


class TicketDeleteView(
        LoginRequiredMixin, OwnerOrSuperuserQuerysetMixin, DeleteView):
    model = Ticket
    template_name = "tickets/ticket_delete.html"
    success_url = reverse_lazy("ticket_list")
    login_url = reverse_lazy("login")


@login_required
def ticket_complete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.is_completed = True
    ticket.save(update_fields=["is_completed"])
    return redirect("ticket_list")
