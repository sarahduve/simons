from django.urls import path
from .views import NucleotideSearchView

urlpatterns = [
    path('search/', NucleotideSearchView.as_view(), name='nucleotide-search'),
]

