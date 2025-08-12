from django.urls import path
from .views import *

urlpatterns = [
    path('payment/<int:booking_id>/', MakePaymentView.as_view(), name='make_payment'),
    path('earnings-summary/', UpdateTechnicianEarningsSummaryAPIView.as_view(), name='update-earnings-summary'),
]