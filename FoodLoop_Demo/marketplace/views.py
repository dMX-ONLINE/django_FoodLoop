
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import FoodListingForm
from .models import FoodListing
from core.utils import universal_delete
from reservations.models import  Review
from django.db.models import Avg, Count



def offerfood(request):
    if request.method == "POST":
        form = FoodListingForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            food = form.save(commit=False)

            if request.user.is_authenticated:
                food.provider = request.user
            else:
                food.provider = None

            food.save()

            messages.success(
                request,
                f"{food.title} has been published successfully!",
            )
            return redirect("marketplace:marketplace")
    else:
        form = FoodListingForm()

    return render(
        request,
        "marketplace/offerfood.html",
        {"form": form},
    )

def marketplace(request):
    foods = FoodListing.objects.annotate(
        average_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    ).order_by('-created_at')
    
    return render(request,'marketplace/marketplace.html',{'foods': foods})


def viewfood(request, pk):
    food = get_object_or_404(
        FoodListing,
        pk=pk,
        is_active=True,
    )

    return render(
        request,
        "marketplace/viewfood.html",
        {"food": food},
    )
    
@login_required
def delete_food(request, pk):

    return universal_delete(
        request=request,
        model=FoodListing,
        pk=pk,
        owner_field='provider',
        redirect_url='accounts:my_listings',
        success_message='Food listing deleted successfully.'
    )
