
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    test_reset_token,
    login,
    signup,
    logout_view,
    profile,
    edit_profile,
    my_listings,
    my_reviews,
    forget_password,
    delete_review,
    delete_food,
    my_reservations
)


app_name = "accounts"


urlpatterns = [

    # ======================================
    # PROFILE
    # ======================================

    path(
        "profile/",
        profile,
        name="profile"
    ),

    path(
        "edit_profile/",
        edit_profile,
        name="edit_profile"
    ),

    path(
        "my_listings/",
        my_listings,
        name="my_listings"
    ),

    path(
        "my_reservations/",
        my_reservations,
        name="my_reservations"
    ),

    path(
        "my_reviews/",
        my_reviews,
        name="my_reviews"
    ),


    # ======================================
    # FORGOT PASSWORD
    # ======================================

    path(
        "forget_password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/forget_password.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="/accounts/password_reset_done/",
        ),
        name="forget_password"
    ),

    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
    "reset/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url="/accounts/password_reset_complete/",
    ),
    name="password_reset_confirm"
    ),

    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),


    # ======================================
    # TEMPORARY TOKEN TEST
    # ======================================

    path(
        "test-reset/<uidb64>/<token>/",
        test_reset_token,
        name="test_reset_token"
    ),


    # ======================================
    # AUTHENTICATION
    # ======================================

    path(
        "signup/",
        signup,
        name="signup"
    ),

    path(
        "login/",
        login,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),


    # ======================================
    # DELETE
    # ======================================

    path(
        "delete_review/<int:pk>/",
        delete_review,
        name="delete_review"
    ),

    path(
        "delete_food/<int:pk>/",
        delete_food,
        name="delete_food"
    ),

]
