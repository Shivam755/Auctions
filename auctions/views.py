from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.forms.widgets import TextInput
from django.http import HttpResponseRedirect
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Category, User, Listing, Comments, Bid, WatchList
from datetime import *


def choices():
    categories = Category.objects.all()
    options = []
    for cat in categories:
        options.append([cat.id, cat])

    return options


class CreateListing(forms.Form):
    title = forms.CharField(max_length=100,
                            widget=TextInput(attrs={'placeholder': 'Title', "class": "text"}))
    des = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Description', 'rows': 5, "cols": 30, "class": "text"}))
    category = forms.ChoiceField(
        widget=forms.Select, choices=choices())
    category.widget.attrs.update({'class': 'text'})
    image_link = forms.URLField(
        max_length=300, required=False)
    image_link.widget.attrs.update(
        {'placeholder': 'Link for image', 'class': 'text'})
    start_bid = forms.FloatField()
    start_bid.widget.attrs.update(
        {'placeholder': 'Starting Bid(in rupees)', 'class': 'text'})


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.filter(buyer=None)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listingPage(request, name, message=""):
    listing = Listing.objects.get(title=name)
    comments = Comments.objects.filter(listing=listing).all()
    message = None
    success = None
    watchlist = []
    if request.user.is_authenticated:
        watchlist = WatchList.objects.filter(
            watched_by=request.user).filter(listing=listing)

    # To handle biddings
    if request.method == 'POST':
        amount = float(request.POST.get('Amount'))
        if amount > listing.start_bid and amount > listing.max_bid:
            user = User.objects.filter(username=request.POST.get('user'))
            # Adding a bid object
            bid = Bid(bid_by=user[0], listing=listing, amount=amount)
            bid.save()
            # Updating max bid for listing
            listing.max_bid = amount
            listing.save(update_fields=['max_bid'])
            message = 'Bid added successfully!!!'
            success = True
        else:
            success = False
            message = 'The bid must be Greater than starting bid and greater than the maximum bid to be valid!!'

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'comments': comments,
        'message': message,
        'watchlist': watchlist,
        'success': success
    })


@login_required
def addComment(request, name):
    if request.method == 'POST':
        user = User.objects.filter(username=request.POST.get('user'))
        listing = Listing.objects.get(title=name)
        comment = Comments(
            commented_by=user[0], message=request.POST.get('message'), listing=listing)
        comment.save()
        return HttpResponseRedirect(reverse('listingPage', args=[name]))
    else:
        return HttpResponseRedirect(reverse('listingPage', args=[name]))


@login_required
def createListing(request):
    if request.method == 'POST':
        form = CreateListing(request.POST)
        if form.is_valid():
            # now = datetime.now()
            category = Category.objects.get(id=form.cleaned_data['category'])
            user = User.objects.get(username=request.POST.get('user'))
            listing = Listing(title=form.cleaned_data['title'], owner=user, description=form.cleaned_data['des'],
                              category=category, image_link=form.cleaned_data['image_link'], start_bid=form.cleaned_data['start_bid'])
            listing.save()
            return render(request, 'auctions/listing.html', {
                'listing': listing,
                'comments': [],
                'message': '',
                'watchlist': []
            })

    form = CreateListing()
    return render(request, 'auctions/createListing.html', {
        'form': form,
        "categories": Category.objects.all()
    })


def winner(request, name):
    if request.method == "POST":
        listing = Listing.objects.get(title=name)
        winning_bid = Bid.objects.filter(
            listing=listing).filter(amount=listing.max_bid)
        listing.buyer = winning_bid[0].bid_by
        listing.close_date = datetime.now()
        listing.save()

    return HttpResponseRedirect(reverse('listingPage', args=[name]))


def listCategories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/showCategories.html', {
        "categories": categories
    })


def showCategory(request, cat):
    category = Category.objects.get(title=cat)
    return render(request, "auctions/categoryListing.html", {
        'listings': Listing.objects.filter(category=category).filter(buyer=None),
        "category": category
    })


@login_required
def showWatchlist(request):
    watchlist = WatchList.objects.filter(watched_by=request.user)
    return render(request, 'auctions/Watchlist.html', {
        'watchlist': watchlist
    })


@login_required
def changeWatchlist(request, name):
    if request.method == 'POST':
        listing = Listing.objects.get(title=name)
        watchlist = WatchList.objects.filter(
            listing=listing).filter(watched_by=request.user)
        if watchlist:
            watchlist[0].delete()
        else:
            watchlist = WatchList(watched_by=request.user, listing=listing)
            watchlist.save()

    return HttpResponseRedirect(reverse('listingPage', args=[name]))
