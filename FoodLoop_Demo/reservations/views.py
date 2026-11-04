
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Avg


from marketplace.models import FoodListing
from .models import Review, Reservation



# ==========================================
# FOOD REVIEWS
# ==========================================

@login_required
def review(request, pk):
    food = get_object_or_404(FoodListing, pk=pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating or not comment:
            messages.error(
                request,
                'Please provide a rating and comment.'
            )
        else:
            try:
                rating = int(rating)
            except (TypeError, ValueError):
                rating = 0

            if 1 <= rating <= 5:
                Review.objects.create(
                    food=food,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )

                messages.success(
                    request,
                    'Your review was submitted successfully.'
                )

                return redirect(
                    'reservations:review',
                    pk=food.pk
                )

            messages.error(
                request,
                'Rating must be between 1 and 5.'
            )

    reviews = Review.objects.filter(
        food=food
    ).order_by('-created_at')

    overall_rating = reviews.aggregate(
        average=Avg('rating')
    )['average'] or 0

    total_reviews = reviews.count()

    rating_counts = {
        rating: reviews.filter(rating=rating).count()
        for rating in range(5, 0, -1)
    }

    return render(
        request,
        'reservations/review.html',
        {
            'food': food,
            'reviews': reviews,
            'overall_rating': overall_rating,
            'total_reviews': total_reviews,
            'rating_counts': rating_counts,
        }
    )


# ==========================================
# CUSTOMER: RESERVE FOOD
# ==========================================

@login_required
def reservation(request, pk):
    food = get_object_or_404(FoodListing, pk=pk)

    if request.method == 'POST':

        # Prevent providers from reserving their own food.
        if food.provider_id == request.user.pk:
            messages.error(
                request,
                'You cannot reserve your own food listing.'
            )
            return redirect(
                'reservations:reservation',
                pk=food.pk
            )

        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1:
            messages.error(
                request,
                'Please enter a valid quantity.'
            )

        elif quantity > food.quantity:
            messages.error(
                request,
                'The requested quantity is not available.'
            )

        else:
            Reservation.objects.create(
                food=food,
                customer=request.user,
                quantity=quantity,
                status='pending'
            )

            messages.success(
                request,
                'Your reservation request has been sent to the provider.'
            )

            return redirect('accounts:my_reservations')

    return render(
        request,
        'reservations/reservation.html',
        {'food': food}
    )


# ==========================================
# PROVIDER: VIEW RESERVATION REQUESTS
# ==========================================

@login_required
def manage_reservations(request):
    all_reservations = Reservation.objects.filter(
        food__provider=request.user
    ).select_related(
        'food',
        'customer',
        'food__location'
    ).order_by('-created_at')


    pending_count = all_reservations.filter(status='pending').count()

    accepted_count = all_reservations.filter(status='accepted').count()

    refused_count = all_reservations.filter(status='refused').count()

    status = request.GET.get('status')

    reservations = all_reservations

    if status in ['pending', 'accepted', 'refused']:
        reservations = reservations.filter(status=status)

    return render(
        request,
        'reservations/manage_reservations.html',
        {
            'reservations': reservations,
            'pending_count': pending_count,
            'accepted_count': accepted_count,
            'refused_count': refused_count,
            'selected_status': status,
        }
    )



# ==========================================
# CUSTOMER: VIEW MY RESERVATIONS
# ==========================================

@login_required
def my_reservations(request):

    reservations = Reservation.objects.filter(
        customer=request.user
    ).select_related(
        'food',
        'food__provider'
    ).order_by('-created_at')
    
    status = request.GET.get('status')
    
    reservations = reservations
    
    if status in ['pending', 'accepted', 'refused']:
        reservations = reservations.filter(status=status)
    

    return render(
        request,
        'accounts/my_reservations.html',
        {
            'reservations': reservations
        }
    )


# ==========================================
# PROVIDER: ACCEPT OR REFUSE RESERVATION
# ==========================================

@login_required
def reservation_action(request, pk):

    if request.method != 'POST':
        return redirect('reservations:manage_reservations')

    with transaction.atomic():

        reservation_item = get_object_or_404(
            Reservation.objects.select_for_update().select_related('food'),
            pk=pk,
            food__provider=request.user
        )

        # Only pending requests can be processed.
        if reservation_item.status != 'pending':
            messages.info(
                request,
                'This reservation has already been processed.'
            )
            return redirect('reservations:manage_reservations')

        action = request.POST.get('action')

        if action == 'accept':

            food = FoodListing.objects.select_for_update().get(
                pk=reservation_item.food_id
            )

            # Check whether enough food remains.
            if reservation_item.quantity > food.quantity:

                messages.error(
                    request,
                    'Not enough food remains to accept this reservation.'
                )

            else:
                # Reduce available food quantity.
                food.quantity -= reservation_item.quantity

                food.save(
                    update_fields=['quantity']
                )

                reservation_item.status = 'accepted'

                reservation_item.save(
                    update_fields=['status', 'updated_at']
                )

                messages.success(
                    request,
                    'Reservation accepted successfully.'
                )

        elif action == 'refuse':

            reservation_item.status = 'refused'

            reservation_item.save(
                update_fields=['status', 'updated_at']
            )

            messages.success(
                request,
                'Reservation refused.'
            )

        else:
            messages.error(
                request,
                'Invalid reservation action.'
            )

    return redirect('reservations:manage_reservations')


# ==========================================
# VIEW FOOD IMAGE
# ==========================================

def view_image(request, pk):

    food = get_object_or_404(
        FoodListing,
        pk=pk
    )

    return render(
        request,
        'reservations/view_image.html',
        {
            'food': food
        }
    )

