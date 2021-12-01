from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import related


class User(AbstractUser):
    pass


class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.title}"


class Listing(models.Model):
    title = models.CharField(max_length=64, default='')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='listings')
    description = models.TextField(default='')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='listing', blank=True, null=True)
    image_link = models.TextField(default='#')
    open_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(blank=True, null=True)
    start_bid = models.FloatField(default=0)
    max_bid = models.FloatField(default=0)
    buyer = models.ForeignKey(User, on_delete=CASCADE,
                              related_name='bought', blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title}"


class Bid(models.Model):
    bid_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bids', null=True)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='bids')
    amount = models.FloatField()
    bid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.amount}({self.bid_by})"


class Comments(models.Model):
    commented_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment')
    message = models.TextField(default='')
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='comment')
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.message}({self.commented_by})"


class WatchList(models.Model):
    watched_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='watchItem')
    listing = models.ForeignKey(
        Listing, on_delete=models.ForeignKey, related_name='watchers')

    def __str__(self) -> str:
        return f"{self.listing}({self.watched_by})"
