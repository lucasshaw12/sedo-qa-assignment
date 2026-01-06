from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


# Extend the existing UserAdmin class to use the new CustomUser model.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # What fields to display in list view
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "num_tickets_assigned",
    )


admin.site.register(CustomUser, CustomUserAdmin)
