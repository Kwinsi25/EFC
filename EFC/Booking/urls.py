from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', GetCartView.as_view(),name='get_cart'),
    path('cart/add/', AddToCartView.as_view(),name='add_to_cart'),
    path('cart/item/<int:item_id>/update/', UpdateCartItemView.as_view(),name='update_cart_item'),
    path('cart/item/<int:item_id>/delete/', DeleteCartItemView.as_view(),name='delete_cart_item'),
    path('cart/clear/', ClearCartView.as_view(),name='clear_cart'),
    path('checkout/', CheckoutView.as_view(),name='checkout'),
    path('verify-otp/', VerifyOtpView.as_view(),name='verify_otp'),
    path('quotation/<int:booking_id>/', QuotationAmountUpdateView.as_view(),name='quotation'),
    path('quotation-decision/<int:booking_id>/', QuotationDecisionView.as_view(),name='quotation-decision'),
    path('job-complete/<int:booking_id>/', JobCompleteView.as_view(),name='job_complete'),
    path('download-bill/<int:booking_id>/', DownloadPDFView.as_view(),name='download_bill'),
    path('checkout/summary/', CheckoutSummaryView.as_view(),name='checkout_summary'),
    path('order-history/', PastOrdersView.as_view(), name='past-orders'),
    path('rebooking/<int:booking_id>/', ReBookingServiceView.as_view(), name='rebooking-service'),
]
