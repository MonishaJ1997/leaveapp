from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("leaves/", views.leave_list, name="leave-list"),
    path("leaves/new/", views.leave_create, name="leave-create"),
    path("leaves/<int:pk>/", views.leave_detail, name="leave-detail"),
    path("leaves/<int:pk>/edit/", views.leave_update, name="leave-update"),
    path("leaves/<int:pk>/delete/", views.leave_delete, name="leave-delete"),

    # ✅ Admin actions
    path("leaves/<int:pk>/approve/", views.approve_leave, name="leave-approve"),
    path("leaves/<int:pk>/reject/", views.reject_leave, name="leave-reject"),
]
