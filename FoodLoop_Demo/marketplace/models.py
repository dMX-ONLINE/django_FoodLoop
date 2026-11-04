from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.

class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Nigeria")

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"

class FoodListing(models.Model):
    CATEGORY_CHOICES = [
        ("cooked", "Cooked Meals"),
        ("bakery", "Bakery"),
        ("produce", "Fresh Produce"),
        ("beverages", "Beverages"),
        ("snacks", "Snacks"),
    ]
    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    location = models.ForeignKey(Location,on_delete=models.SET_NULL, related_name="food_listings", null=True, blank=True)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    pickup_start = models.DateTimeField()
    expiry_time = models.DateTimeField()
    image = models.ImageField(
        upload_to="food_listings/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return (
            self.is_active
            and self.quantity > 0
            and self.expiry_time > timezone.now()
        )
    