
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from django.db.models import Avg, Count

from core.utils import universal_delete
from marketplace.models import FoodListing
from reservations.models import Reservation, Review


from .forms import (
    SignupForm,
    LoginForm,
    AccountUpdateForm,
    ProfileUpdateForm
)
from .models import UserProfile


User = get_user_model()


# ==========================================
# TEMPORARY PASSWORD RESET DEBUGGING
# ==========================================

def test_reset_token(request, uidb64, token):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)

        result = default_token_generator.check_token(
            user,
            token
        )

        return HttpResponse(
            f"User: {user.username}<br>"
            f"Email: {user.email}<br>"
            f"Token valid: {result}"
        )

    except Exception as e:
        return HttpResponse(f"Error: {e}")


# ==========================================
# LOGIN
# ==========================================

def login(request):

    if request.user.is_authenticated:
        return redirect("core:index")

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            auth_login(
                request,
                form.get_user()
            )

            return redirect("core:index")

    else:
        form = LoginForm(request)

    return render(
        request,
        "accounts/login.html",
        {"form": form}
    )


# ==========================================
# SIGNUP
# ==========================================

def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            profile, created = UserProfile.objects.get_or_create(
                user=user
            )

            profile.phone_number = form.cleaned_data.get(
                "phone_number", ""
            ).strip()

            profile.save()

            messages.success(
                request,
                "Your FoodLoop account has been created successfully. "
                "You can now log in."
            )

            return redirect("accounts:login")

    else:
        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form}
    )


# ==========================================
# FORGOT PASSWORD
# ==========================================

def forget_password(request):

    return render(
        request,
        "accounts/forget_password.html"
    )


# ==========================================
# PROFILE
# ==========================================

@login_required
def profile(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    my_listings_count = FoodListing.objects.filter(
        provider=request.user
    ).count()

    my_reservations_count = Reservation.objects.filter(
        customer=request.user
    ).count()
    
    review_data = Review.objects.filter(user=request.user).aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    average_rating = review_data['average_rating'] or 0
    total_reviews = review_data['total_reviews']

    my_reviews_count = Review.objects.filter(
        user=request.user
    ).count()

    context = {
        "profile": profile,
        "account": request.user,
        "my_listings_count": my_listings_count,
        "my_reservations_count": my_reservations_count,
        "my_reviews_count": my_reviews_count,
        'total_reviews': total_reviews,
        'average_rating': average_rating
    }

    return render(
        request,
        "accounts/profile.html",
        context
    )


# ==========================================
# MY LISTINGS
# ==========================================

@login_required
def my_listings(request):

    foods = FoodListing.objects.filter(
        provider=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/my_listings.html",
        {"foods": foods}
    )


# ==========================================
# MY RESERVATIONS
# ==========================================

@login_required
def my_reservations(request):

    reservations = Reservation.objects.filter(
        customer=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/my_reservations.html",
        {"reservations": reservations}
    )


# ==========================================
# MY REVIEWS
# ==========================================

@login_required
def my_reviews(request):

    reviews = Review.objects.filter(
        user=request.user
    ).select_related(
        "food"
    ).order_by("-created_at")

    return render(
        request,
        "accounts/my_reviews.html",
        {"reviews": reviews}
    )


# ==========================================
# EDIT PROFILE
# ==========================================

@login_required
def edit_profile(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        account_form = AccountUpdateForm(
            request.POST,
            instance=request.user
        )

        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if account_form.is_valid() and profile_form.is_valid():

            account_form.save()
            profile_form.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("accounts:profile")

    else:

        account_form = AccountUpdateForm(
            instance=request.user
        )

        profile_form = ProfileUpdateForm(
            instance=profile
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "account_form": account_form,
            "profile_form": profile_form,
            "profile": profile,
        }
    )


# ==========================================
# LOGOUT
# ==========================================

@require_POST
@login_required
def logout_view(request):

    auth_logout(request)

    messages.success(
        request,
        "You have logged out successfully."
    )

    return redirect("core:welcome")


# ==========================================
# DELETE REVIEW
# ==========================================

@login_required
def delete_review(request, pk):

    return universal_delete(
        request=request,
        model=Review,
        pk=pk,
        owner_field="user",
        redirect_url="accounts:my_reviews",
        success_message="Review deleted successfully."
    )


# ==========================================
# DELETE FOOD
# ==========================================

@login_required
def delete_food(request, pk):

    return universal_delete(
        request=request,
        model=FoodListing,
        pk=pk,
        owner_field="provider",
        redirect_url="accounts:my_listings",
        success_message="Food deleted successfully."
    )
