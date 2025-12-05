from django.views.generic import ListView
from .models import Ticket

class TicketListView(ListView):
	model = Ticket
	template_name = 'tickets/ticket_list.html'