from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Payment
from Booking.models import *

class MakePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        user = request.user

        try:
            booking = ServiceBook.objects.get(id=booking_id, user=user)
        except ServiceBook.DoesNotExist:
            return Response({"status": 404, "message": "Booking not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != 'complete':
            return Response({"status": 400, "message": "Payment can only be made after job is completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if payment already exists
        if Payment.objects.filter(order=booking).exists():
            return Response({"status": 400, "message": "Payment already recorded for this booking."}, status=status.HTTP_400_BAD_REQUEST)

        method = request.data.get("method")
        received_by = request.data.get("received_by")
        upi = request.data.get("upi", None)

        if not method or not received_by:
            return Response({"status": 400, "message": "Payment method and received_by are required."}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            order=booking,
            amount=booking.quatation_amt,
            method=method,
            received_by=received_by,
            upi=upi,
            status="paid"
        )

        return Response({
            "status": 200,
            "message": "Payment successful.",
            "data": {
                "payment_id": payment.id,
                "booking_id": booking.id,
                "amount": payment.amount,
                "method": payment.method,
                "received_by": payment.received_by,
                "status": payment.status,
                "created": payment.created_date,
            }
        })
