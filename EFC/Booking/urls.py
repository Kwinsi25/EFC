from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', GetCartView.as_view(),name='get_cart'),
    path('cart/add/', AddToCartView.as_view(),name='add_to_cart'),
    path('cart/item/<int:item_id>/update/', UpdateCartItemView.as_view(),name='update_cart_item'),
    path('cart/item/<int:item_id>/delete/', DeleteCartItemView.as_view(),name='delete_cart_item'),
    path('cart/clear/', ClearCartView.as_view(),name='clear_cart'),
    path('checkout/', CheckoutView.as_view(),name='checkout'),
    path('checkout/summary/', CheckoutSummaryView.as_view(),name='checkout_summary'),
    path('bookings/', BookingHistoryView.as_view(),name='booking_history'),
    path('booking/<int:booking_id>/', BookingDetailView.as_view(),name='booking_detail'),
    path('booking/<int:booking_id>/technician/', AssignedTechnicianView.as_view(),name='assigned_technician'),
    path('booking/<int:booking_id>/status/', UpdateBookingStatusView.as_view(),name='update_booking_status'),
    path('booking/<int:booking_id>/status/view/', BookingStatusView.as_view(),name='booking_status_view'),
    path('booking/<int:booking_id>/assign-technician/', AssignTechnicianView.as_view(),name='assign_technician'),
    path('booking/<int:booking_id>/arrived/', MarkTechnicianArrivedView.as_view(),name='mark_technician_arrived'),
    path('booking/<int:booking_id>/verify-otp/', VerifyServiceOTPView.as_view(),name='verify_service_otp'),
    path('booking/<int:booking_id>/complete/', MarkJobCompleteView.as_view(),name='mark_job_complete'),
    path('booking/<int:booking_id>/generate-bill/', GenerateBillView.as_view()),
    path('booking/<int:booking_id>/download-bill/', DownloadBillView.as_view()),
    path('history/', OrderHistoryView.as_view(), name='order-history'),
]
