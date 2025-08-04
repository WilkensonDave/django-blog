from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.registerView, name="registerView"),
    path("login/", views.loginView, name="loginView"),
    path("all-posts/", views.all_posts, name="all-posts"),
    path("post/<slug:slug>", views.post_details, name="post_details"),
    path("edit_comment/<int:pk>", views.edit_comment, name="edit_comment"),
    path("delete_comment/<int:pk>", views.delete_comment, name="delete_comment"),
    path("logout/", views.logoutView, name="logoutView"),
    path("unauthorize/", views.unauthorize, name="unauthorize"),
    path("forgetpassord/", views.forgetPassword, name="forget-password"),
    path("reset-password-link/<str:reset_id>", views.passwordresetsend, name="password-reset-send"),
    path("resetPassword/<str:reset_id>", views.resetPasword, name="reset-password"),
    path("profile", views.profile, name="profile"),
    path("readlater", views.readlater, name="readlater")
]
