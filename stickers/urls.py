from django.urls import path
from .views import RedemptionView, TransactionIngestView
from .views import ShopperDetailView 
from .views import StatsView,portal_view

urlpatterns = [
    path("transactions/", TransactionIngestView.as_view(), name="transaction-ingest"),
    path("shoppers/<str:shopper_id>/", ShopperDetailView.as_view()),
    path("stats/", StatsView.as_view()),
    path("redeem/", RedemptionView.as_view()),
    
    path("portal/", portal_view, name="portal"),
]