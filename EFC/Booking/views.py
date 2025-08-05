from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from Accounts.models import CustomerProfile, Address
from Services.models import SubCategory
from .models import Cart, ServiceCart, ServiceBook
from Wallet.models import Payment
from .serializers import *
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.core.files.storage import default_storage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from django.http import FileResponse


class AddToCartView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        service_id = request.data.get("service")
        qty = int(request.data.get("qty", 1))
        num_of_tech = int(request.data.get("num_of_tech", 1))

        user = get_object_or_404(CustomerProfile, id=user_id)
        service = get_object_or_404(SubCategory, id=service_id)
        price = float(service.price)

        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = ServiceCart.objects.get_or_create(cart=cart, service=service)

        item.qty = qty
        item.num_of_tech = num_of_tech
        item.price = price
        item.total_price = qty * num_of_tech * price
        item.save()

        return Response({
            "status": 201,
            "message": "Item added to cart" if created else "Cart updated",
            "data": ServiceCartSerializer(item).data
        })
        

class GetCartView(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")
        user = get_object_or_404(CustomerProfile, id=user_id)
        cart = Cart.objects.filter(user=user).first()

        if not cart:
            return Response({
                "status": 200,
                "message": "Cart is empty",
                "data": {"items": [], "total": 0}
            })

        items = ServiceCart.objects.filter(cart=cart)
        total = sum(item.total_price for item in items)
        data = ServiceCartSerializer(items, many=True).data

        return Response({
            "status": 200,
            "message": "Cart fetched",
            "data": {
                "items": data,
                "total": total
            }
        })
    
class UpdateCartItemView(APIView):
    def patch(self, request, item_id):
        item = get_object_or_404(ServiceCart, id=item_id)

        qty = request.data.get("qty", item.qty)
        num_of_tech = request.data.get("num_of_tech", item.num_of_tech)

        item.qty = int(qty)
        item.num_of_tech = int(num_of_tech)
        item.total_price = item.qty * item.num_of_tech * item.price
        item.save()

        return Response({
            "status": 200,
            "message": "Cart item updated",
            "data": ServiceCartSerializer(item).data
        })


class DeleteCartItemView(APIView):
    def delete(self, request, item_id):
        item = get_object_or_404(ServiceCart, id=item_id)
        item.delete()
        return Response({
            "status": 200,
            "message": "Cart item removed"
        })


class ClearCartView(APIView):
    def delete(self, request):
        user_id = request.GET.get("user_id")
        user = get_object_or_404(CustomerProfile, id=user_id)
        cart = Cart.objects.filter(user=user).first()

        if cart:
            cart.services.all().delete()

        return Response({
            "status": 200,
            "message": "Cart cleared"
        })
    

class CheckoutView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        address_id = request.data.get("address_id")
        payment_method = request.data.get("method")  # UPI, COD, etc.
        upi = request.data.get("upi", "")
        received_by = request.data.get("received_by", "platform")

        user = get_object_or_404(CustomerProfile, id=user_id)
        address = get_object_or_404(Address, id=address_id)
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.services.exists():
            return Response({"status": 400, "message": "Cart is empty"}, status=400)

        bookings = []
        total_amount = 0

        for item in cart.services.all():
            booking = ServiceBook.objects.create(
                user=user,
                service=item.service,
                technician_required=item.num_of_tech,
                status='assign',
                is_scheduled=False
            )
            total_amount += item.total_price
            bookings.append(booking)

        # Save Payment
        Payment.objects.create(
            order=bookings[0],  
            amount=total_amount,
            upi=upi,
            method=payment_method,
            received_by=received_by,
            bill_requested=False
        )

        # Clear the cart
        cart.services.all().delete()

        return Response({
            "status": 200,
            "message": "Booking successful",
            "data": {
                "total_amount": total_amount,
                "payment_method": payment_method,
                "bookings": [b.id for b in bookings]
            }
        })
    
class CheckoutSummaryView(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")
        user = get_object_or_404(CustomerProfile, id=user_id)
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.services.exists():
            return Response({
                "status": 400,
                "message": "Cart is empty",
                "data": {}
            }, status=400)

        cart_items = ServiceCart.objects.filter(cart=cart)
        total = sum(item.total_price for item in cart_items)
        items_data = ServiceCartSerializer(cart_items, many=True).data

        addresses = Address.objects.filter(user=user)

        address_list = [{
            "id": addr.id,
            "address": addr.address,
            "city": addr.city,
            "state": addr.state,
            "pinCode": addr.pincode,
            "isDefault": addr.is_default
        } for addr in addresses]

        return Response({
            "status": 200,
            "message": "Checkout summary fetched",
            "data": {
                "items": items_data,
                "total_amount": total,
                "addresses": address_list
            }
        })
    
class BookingHistoryView(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")
        user = get_object_or_404(CustomerProfile, id=user_id)

        bookings = ServiceBook.objects.filter(user=user).order_by('-created_date')
        serializer = BookingListSerializer(bookings, many=True, context={'request': request})

        return Response({
            "status": 200,
            "message": "Booking history fetched",
            "data": serializer.data
        })
    
class BookingDetailView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)

        data = {
            "id": booking.id,
            "service": booking.service.name,
            "technician_required": booking.technician_required,
            "status": booking.status,
            "assigned_technician": booking.assigned_technician.username if booking.assigned_technician else None,
            "photo": request.build_absolute_uri(booking.photo.url) if booking.photo else None,
            "comment": booking.comment,
            "is_bill_generated": booking.is_bill_generated,
            "pdf_url": booking.pdf_url,
            "created_at": booking.created_date
        }

        return Response({
            "status": 200,
            "message": "Booking details fetched",
            "data": data
        })


class AssignedTechnicianView(APIView):
    """
    GET: View assigned technician details
    """
    def get(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)
        tech = booking.assigned_technician

        if not tech:
            return Response({
                "status": 404,
                "message": "Technician not assigned yet",
                "data": {}
            }, status=404)

        rating = tech.reviews_received.filter(is_approved=True).aggregate(
            avg=models.Avg('rating'))['avg'] or 0

        data = {
            "id": tech.id,
            "name": tech.username,
            "photo": request.build_absolute_uri(tech.profile_image.url) if tech.profile_image else None,
            "type": "Agency" if tech.role == "agency" else "Individual",
            "rating": round(rating, 1),
            "contact": tech.mobile if tech.role != "admin" else None  # optional
        }

        return Response({
            "status": 200,
            "message": "Technician info fetched",
            "data": data
        })

class UpdateBookingStatusView(APIView):
    """
    PATCH: Update booking status to assigned, arriving, complete, cancel
    """
    def patch(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)
        new_status = request.data.get("status")

        valid_status = ['assign', 'arriving', 'complete', 'cancel']
        if new_status not in valid_status:
            return Response({
                "status": 400,
                "message": "Invalid status. Use: assign, arriving, complete, cancel"
            }, status=400)

        booking.status = new_status
        booking.save()

        return Response({
            "status": 200,
            "message": f"Booking status updated to {new_status}"
        })

class BookingStatusView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)
        return Response({
            "status": 200,
            "message": "Booking status fetched",
            "data": {
                "booking_id": booking.id,
                "status": booking.status
            }
        })


class AssignTechnicianView(APIView):
    """
    PATCH: Assign a technician manually to a booking
    Body:
    {
        "technician_id": 5
    }
    """
    def patch(self, request, booking_id):
        technician_id = request.data.get("technician_id")
        if not technician_id:
            return Response({
                "status": 400,
                "message": "technician_id is required"
            }, status=400)

        booking = get_object_or_404(ServiceBook, id=booking_id)
        technician = get_object_or_404(CustomerProfile, id=technician_id, role='electrician')

        booking.assigned_technician = technician
        booking.save()

        return Response({
            "status": 200,
            "message": f"Technician '{technician.username}' assigned to booking #{booking.id}"
        })
    
class MarkTechnicianArrivedView(APIView):
    """
    PATCH: Technician marks arrival at user's location
    """
    def patch(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)

        if booking.status != "arriving":
            return Response({
                "status": 400,
                "message": f"Technician must be in 'arriving' state. Current: {booking.status}"
            })

        booking.arrived_at = timezone.now()
        booking.save()

        return Response({
            "status": 200,
            "message": "Technician marked as arrived"
        })

class VerifyServiceOTPView(APIView):
    """
    PATCH: Verify OTP to start service
    Body: { "otp": "123456", "verified_by": 7 }
    """
    def patch(self, request, booking_id):
        entered_otp = request.data.get("otp")
        verified_by = request.data.get("verified_by")

        booking = get_object_or_404(ServiceBook, id=booking_id)

        if not booking.service_start_otp:
            return Response({"status": 400, "message": "OTP not generated for this booking"})

        if str(entered_otp) != str(booking.service_start_otp):
            return Response({"status": 400, "message": "Invalid OTP"})

        booking.otp_verified_at = timezone.now()
        booking.otp_verified_by_id = verified_by
        booking.job_started_at = timezone.now()
        booking.status = "complete"  # or "in-progress" if you want that in between
        booking.save()

        return Response({
            "status": 200,
            "message": "OTP verified, service started"
        })

class MarkJobCompleteView(APIView):
    """
    PATCH: Technician marks service as completed
    Body: {
        "comment": "AC fixed",
        "photo": <image file>
    }
    """
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)

        comment = request.data.get("comment")
        photo = request.FILES.get("photo")

        booking.comment = comment
        if photo:
            booking.photo = photo
        booking.status = "complete"
        booking.save()

        return Response({
            "status": 200,
            "message": "Service marked as completed"
        })


class GenerateBillView(APIView):
    def post(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)
        charges = request.data.get("charges", {})

        # Get user info
        user = booking.user
        address_obj = Address.objects.filter(user=user, is_default=True).first()

        # Get service info
        service = booking.service
        technician = booking.assigned_technician

        # Compose PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph("INVOICE / SERVICE BILL", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Customer Info
        elements.append(Paragraph("<b>Customer Details:</b>", styles['Heading4']))
        elements.append(Paragraph(f"Name: {user.username}", styles['Normal']))
        elements.append(Paragraph(f"Mobile: {user.mobile}", styles['Normal']))
        if address_obj:
            elements.append(Paragraph(f"Address: {address_obj.address}, {address_obj.city}, {address_obj.state} - {address_obj.pincode}", styles['Normal']))
        else:
            elements.append(Paragraph("Address: Not available", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Service Info
        elements.append(Paragraph("<b>Service Details:</b>", styles['Heading4']))
        elements.append(Paragraph(f"Service: {service.name}", styles['Normal']))
        elements.append(Paragraph(f"Technicians Required: {booking.technician_required}", styles['Normal']))
        elements.append(Paragraph(f"Quantity: 1", styles['Normal']))  # Assuming single unit per ServiceBook
        if technician:
            elements.append(Paragraph(f"Assigned Technician: {technician.username}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Charges
        elements.append(Paragraph("<b>Charges:</b>", styles['Heading4']))
        charge_data = [[key.replace("_", " ").title(), f"₹{value}"] for key, value in charges.items()]
        table = Table(charge_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # Footer
        elements.append(Paragraph("Thank you for choosing Estate Fix & Care!", styles['Normal']))
        elements.append(Paragraph("For support, contact: support@efc.com", styles['Normal']))

        # Build and save
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        file_path = f"bills/booking_{booking.id}.pdf"
        default_storage.save(file_path, ContentFile(pdf))

        booking.pdf_url = file_path
        booking.is_bill_generated = True
        booking.save()

        return Response({
            "status": 200,
            "message": "Bill generated successfully",
            "pdf_url": file_path
        })
       
class DownloadBillView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(ServiceBook, id=booking_id)
        if not booking.pdf_url or not default_storage.exists(booking.pdf_url):
            return Response({"status": 404, "message": "Bill not found"}, status=404)

        file = default_storage.open(booking.pdf_url, 'rb')
        return FileResponse(file, as_attachment=True, filename=f"Booking_{booking_id}_Bill.pdf")
    
class OrderHistoryView(APIView):
    permission_classes = [permissions.AllowAny]  # No token required for now

    def get(self, request):
        user_id = request.query_params.get('user')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=400)

        bookings = ServiceBook.objects.filter(user_id=user_id).order_by('-scheduled_date_time')
        serializer = OrderHistorySerializer(bookings, many=True)
        return Response(serializer.data)