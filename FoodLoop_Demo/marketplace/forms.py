from django import forms
from django.utils import timezone
from .models import FoodListing


class FoodListingForm(forms.ModelForm):
    class Meta:
        model = FoodListing
        fields = [
            "title",
            "description",
            "category",
            "price",
            "quantity",
            "location",
            "pickup_start",
            "expiry_time",
            "image",
        ]
        widgets = {
            "pickup_start": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "expiry_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 5}
            ),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError(
                "Price cannot be negative."
            )
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError(
                "Quantity must be at least one."
            )
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("pickup_start")
        expiry = cleaned_data.get("expiry_time")

        if start and start < timezone.now():
            self.add_error(
                "pickup_start",
                "Pickup cannot start in the past.",
            )

        if start and expiry and expiry <= start:
            self.add_error(
                "expiry_time",
                "Expiry must be after pickup starts.",
            )

        return cleaned_data
