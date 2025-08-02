from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    wishlist = models.ManyToManyField(
        "AuctionListing",
        blank=True,
        related_name="whishlisted_by"
    )


class Category(models.Model):
    category_code = models.CharField(max_length=5, unique=True)
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name

    class Meta:
        ordering = ['category_name']
        verbose_name_plural = "Categories"


class AuctionListing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=2000)
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name="auction_listings"
    )
    starting_bid = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="auction_listings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    closing_bid = models.OneToOneField(
        "Bid",
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    def get_current_price(self):
        """Returns the highest bid amount or the starting bid."""
        if self.bids.exists():
            return self.bids.order_by("-amount").first().amount

        return self.starting_bid

    def __str__(self):
        return self.title


class Bid(models.Model):
    auction_listing = models.ForeignKey(
        AuctionListing,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="bids"
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"


class Comment(models.Model):
    auction_listing = models.ForeignKey(
        AuctionListing,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auction_listing} - {self.user} - {self.content[:20]}"
