from django.urls import path
from .views import TicketListView, TicketCreateView, TicketUpdateView, TicketDeleteView

urlpatterns = [
	path('', TicketListView.as_view(), name='ticket_list'),
	path('add', TicketCreateView.as_view(), name='ticket_add'),
	path('<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket_edit'),
	path('<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket_delete'),

]
