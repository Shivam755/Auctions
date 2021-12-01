from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<str:name>", views.listingPage, name='listingPage'),
    path('listing/<str:name>/comments', views.addComment, name='addComment'),
    path('listing/<str:name>/close', views.winner, name='closeListing'),
    path('createListing', views.createListing, name='createListing'),
    path('categories', views.listCategories, name='listCategories'),
    path('categories/<str:cat>', views.showCategory, name='showCategory'),
    path('watchlist', views.showWatchlist, name='showWatchlist'),
    path('listing/<str:name>/watchlist',
         views.changeWatchlist, name='changeWatchlist')
]
