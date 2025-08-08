from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Payment
from Booking.models import *
from django.utils import timezone
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

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
        bill_requested = request.data.get("bill_requested", 0) == 1
       
        if not method or not received_by:
            return Response({"status": 400, "message": "Payment method and received_by are required."}, status=status.HTTP_400_BAD_REQUEST)

            
        payment = Payment.objects.create(
            order=booking,
            amount=booking.quatation_amt,
            upi=upi,
            status="paid",
            method=method,
            received_by=received_by,
            bill_requested=bill_requested
        )
        pdf_url = None
        # Update bill_requested if user set to true
        if bill_requested:
            booking.is_bill_generated = True
            booking.save(update_fields=["is_bill_generated"])

            # Generate PDF
            bill_dir = os.path.join(settings.MEDIA_ROOT, 'bills')
            os.makedirs(bill_dir, exist_ok=True)
            pdf_filename = f"{user}_service_bill_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
            pdf_path = os.path.join(bill_dir, pdf_filename)

            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            content = []

            content.append(Paragraph("<b>Service Payment Receipt</b>", styles['Title']))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Customer Name: {booking.user.username}", styles['Normal']))
            content.append(Paragraph(f"Customer Phone: {getattr(booking.user, 'phone', 'N/A')}", styles['Normal']))
            content.append(Paragraph(f"Address: {getattr(booking, 'address', 'N/A')}", styles['Normal']))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Electrician: {booking.assigned_technician.username}", styles['Normal']))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Service: {booking.service.name}", styles['Normal']))
            content.append(Paragraph(f"Description: {booking.service.description}", styles['Normal']))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Quotation Amount: ₹{booking.quatation_amt}", styles['Normal']))
            content.append(Paragraph(f"Electrician Charge: ₹100.0", styles['Normal']))                                   #here we added a normal charge
            content.append(Paragraph(f"Total Paid Amount: ₹{booking.quatation_amt + 100}", styles['Normal']))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Date: {timezone.now().strftime('%Y-%m-%d')}", styles['Normal']))
            content.append(Spacer(1, 20))
            content.append(Paragraph("Thank you for using our service!", styles['Italic']))

            doc.build(content)

            pdf_url = f"bills/{pdf_filename}"
            # Save the PDF URL in the service booking
            booking.pdf_url = pdf_url
            booking.save(update_fields=["pdf_url"])


        # If UPI is provided, generate a PDF receipt
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
                "bill_pdf_url": pdf_url,
                "created": payment.created_date,
            }
        })
