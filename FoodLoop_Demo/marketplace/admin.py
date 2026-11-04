from django.contrib import admin
from .models import FoodListing, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'address',
        'city',
        'state',
        'country',
    )

    list_filter = (
        'city',
        'state',
        'country',
    )

    search_fields = (
        'address',
        'city',
        'state',
    )


@admin.register(FoodListing)
class FoodListingAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'price',
        'location',
        "pickup_start",
        'quantity',
        'provider',
        'expiry_time',
    )

    list_filter = ('category',)

    search_fields = (
        'title',
        'description',
    )