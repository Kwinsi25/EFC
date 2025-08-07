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
    path('quotation/<int:booking_id>/', QuotationDecisionView.as_view(),name='quotation'),
    path('job-complete/<int:booking_id>/', JobCompleteView.as_view(),name='job_complete'),
    path('download-bill/<int:booking_id>/', DownloadBillPDFView.as_view(),name='download_bill'),
    path('checkout/summary/', CheckoutSummaryView.as_view(),name='checkout_summary'),
    path('booking-history/', BookingHistoryView.as_view(),name='booking_history'),
    path('<int:booking_id>/', BookingDetailView.as_view(),name='booking_detail'),
    # path('<int:booking_id>/technician/', AssignedTechnicianView.as_view(),name='assigned_technician'),
    # path('<int:booking_id>/status/', UpdateBookingStatusView.as_view(),name='update_booking_status'),
    # path('<int:booking_id>/status/view/', BookingStatusView.as_view(),name='booking_status_view'),
    # path('<int:booking_id>/assign-technician/', AssignTechnicianView.as_view(),name='assign_technician'),
    # path('<int:booking_id>/arrived/', MarkTechnicianArrivedView.as_view(),name='mark_technician_arrived'),
    # path('<int:booking_id>/verify-otp/', VerifyServiceOTPView.as_view(),name='verify_service_otp'),
    # path('<int:booking_id>/complete/', MarkJobCompleteView.as_view(),name='mark_job_complete'),
    # path('<int:booking_id>/generate-bill/', GenerateBillView.as_view()),
    # path('<int:booking_id>/download-bill/', DownloadBillView.as_view()),
    # path('history/', OrderHistoryView.as_view(), name='order-history'),
]
