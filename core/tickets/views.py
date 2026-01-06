from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ticket


class TicketListView(ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = [
        'title',
        'body',
        'author',
    ]
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("ticket_list")
    login_url = reverse_lazy("login")


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    fields = TicketCreateView.fields
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("ticket_list")
    login_url = reverse_lazy("login")


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "tickets/ticket_delete.html"
    success_url = reverse_lazy("ticket_list")
    login_url = reverse_lazy("login")
