from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="search-engines"),
    path("search_results/",views.display, name="search-result"),
   # path("search_lyrics/", views.search_lyrics, name="search-lyrics"),
    path("filters/", views.filters, name="apply-filters"),
    path("lyrics/",views.getLyrics,name="get-lyrics"),
    path("recommendations/",views.getRecommendations, name ="get-recommendations")
]