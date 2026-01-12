from django.urls import path

from user.views import (
    UserCreateView,
    UserManageView
)

app_name = "user"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("me/", UserManageView.as_view(), name="manage_user"),
]
