from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from Accounts.models import CustomerProfile, Address
from Services.models import SubCategory
from .models import Cart, ServiceCart, ServiceBook
from .serializers import *
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
import random,os
from django.conf import settings
from reportlab.lib.pagesizes import letter
from django.http import FileResponse, Http404
from Services.models import *
# from .models import Cart, ServiceBook, Address  # adjust import paths as needed


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # user_id = request.data.get("user_id")
        service_id = request.data.get("service")
        qty = int(request.data.get("qty", 1))
        num_of_tech = int(request.data.get("num_of_tech", 1))

        # user = get_object_or_404(CustomerProfile, id=user_id)
        user = request.user
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
    permission_classes = [permissions.IsAuthenticated]  # Ensure token is required

    def get(self, request):
        user = request.user  # ✅ Authenticated user from token
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
    permission_classes = [permissions.IsAuthenticated]  #Require JWT token

    def patch(self, request, item_id):
        user = request.user  # Get user from token

        item = get_object_or_404(ServiceCart, id=item_id)

        # 🔒 Ensure the item belongs to the user's cart
        if item.cart.user != user:
            return Response({
                "status": 403,
                "message": "You do not have permission to update this item"
            }, status=403)

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
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        user = request.user  #User from token

        item = get_object_or_404(ServiceCart, id=item_id)

        #Ensure the cart item belongs to the authenticated user
        if item.cart.user != user:
            return Response({
                "status": 403,
                "message": "You do not have permission to delete this item"
            }, status=403)

        item.delete()
        return Response({
            "status": 200,
            "message": "Cart item removed"
        })

class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user  # 🔐 User from token
        cart = Cart.objects.filter(user=user).first()

        if cart:
            cart.services.all().delete()

        return Response({
            "status": 200,
            "message": "Cart cleared"
        })    

class CheckoutSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # user_id = request.GET.get("user_id")
        # user = get_object_or_404(CustomerProfile, id=user_id)
        user = request.user

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
    

class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
    
        if not cart or not cart.services.exists():
            return Response({"status": 400, "message": "Cart is empty"}, status=400)

        # Get default address
        default_address = Address.objects.filter(user=user, is_default=True).first()
        if not default_address:
            return Response({"status": 400, "message": "No default address found"}, status=400)

        bookings = []
        total_amount = 0
        assigned_count = 0

        for item in cart.services.all():
            service_name = item.service.name.strip().lower()

            # Step 1: Try within 3km
            electrician = self.find_matching_electrician(service_name, km_limit=3)

            # Step 2: If not found, try within 5km
            if not electrician:
                electrician = self.find_matching_electrician(service_name, km_limit=5)

            # ✅ Set status based on assignment
            booking_status = 'assign' if electrician else 'pending'

            # Generate OTP
            otp = str(random.randint(1000, 9999))

            booking = ServiceBook.objects.create(
                user=user,
                service=item.service,
                technician_required=item.num_of_tech,
                status=booking_status,
                is_scheduled=False,
                service_start_otp=otp,
                otp_generated_at=timezone.now(),
                assigned_technician=electrician if electrician else None
            )

            total_amount += item.total_price

            if electrician:
                assigned_count += 1
                msg = f"Electrician '{electrician.username}' assigned."
            else:
                msg = "No electrician found within 5km."

            bookings.append({
                "id": booking.id,
                "service": item.service.name,
                "otp": otp,
                "assigned_technician": electrician.username if electrician else None,
                "assignment_message": msg,
                "status": booking_status
            })

        # Clear cart
        cart.services.all().delete()

        if assigned_count == 0:
            final_msg = "Booking confirmed"
        else:
            final_msg = "Booking confirmed"

        return Response({
            "status": 200,
            "message": final_msg,
            "data": {
                "total_amount": total_amount,
                "bookings": bookings,
                "default_address": {
                    "label": default_address.label,
                    "address": default_address.address,
                    "city": default_address.city,
                    "state": default_address.state,
                    "pincode": default_address.pincode,
                }
            }
        })

    def find_matching_electrician(self, service_name, km_limit):
        electricians = CustomerProfile.objects.filter(role='electrician')

        service_keywords = [word.strip().lower() for word in service_name.split() if word.strip()]

        for electrician in electricians:
            if electrician.service_skill:
                skill_keywords = []
                for skill_phrase in electrician.service_skill.split(','):
                    words = skill_phrase.strip().lower().split()
                    skill_keywords.extend(words)

                #Match if ANY service word exists in ANY skill word
                if any(word in skill_keywords for word in service_keywords):
                    if electrician.service_km and electrician.service_km <= km_limit:
                        return electrician

        return None



class VerifyOtpView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        booking_id = request.data.get("booking_id")
        entered_otp = request.data.get("otp")
        print(user, booking_id, entered_otp)
        if not booking_id or not entered_otp:
            return Response({"status": 400, "message": "Booking ID and OTP are required"}, status=400)

        try:
            booking = ServiceBook.objects.get(id=booking_id, assigned_technician=user)
        except ServiceBook.DoesNotExist:
            return Response({"status": 404, "message": "Booking not found or not assigned to you"}, status=404)

        if booking.service_start_otp != entered_otp:
            return Response({"status": 401, "message": "Invalid OTP"}, status=401)

        # OTP is valid
        booking.otp_verified_at = timezone.now()
        booking.otp_verified_by = user
        booking.status = "arriving"
        booking.save()

        return Response({
            "status": 200,
            "message": "OTP verified successfully. Status updated to arriving.",
            "data": {
                "booking_id": booking.id,
                "verified_at": booking.otp_verified_at,
                "verified_by": user.username,
                "status": booking.status
            }
        })


class QuotationAmountUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        user = request.user

        booking = get_object_or_404(ServiceBook, id=booking_id)

        # Optional: prevent update if already approved/rejected
        if booking.action in ['approve', 'reject']:
            return Response({
                "status": 403,
                "message": "Quotation decision already made. Cannot update amount."
            }, status=403)

        # Calculate quotation amount using service price + electrician charge
        base_price = getattr(booking.service, 'price', 0.0)
        electrician_charge = 100.0  # You can make this dynamic later if needed
        total_amount = float(base_price) + electrician_charge

        booking.quatation_amt = total_amount
        booking.save()

        return Response({
            "status": 200,
            "message": "Quotation amount calculated and saved successfully.",
            "quotation_amt": total_amount,
            "base_price": base_price,
            "electrician_charge": electrician_charge
        })
    
class QuotationDecisionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        user = request.user
        decision = request.data.get('user_approved')  # Expecting true/false from frontend

        if decision is None:
            return Response({"status": 400, "message": "'user_approved' field is required (true or false)."}, status=400)

        try:
            booking = ServiceBook.objects.get(id=booking_id, user=user)
        except ServiceBook.DoesNotExist:
            return Response({"status": 404, "message": "Booking not found or access denied."}, status=404)

        if not booking.otp_verified_at:
            return Response({"status": 403, "message": "OTP not yet verified for this booking."}, status=403)

        # Convert decision to boolean safely
        decision_bool = str(decision).lower() in ['true', '1', 'yes']

        if decision_bool:  # Approved
            # base_price = getattr(booking.service, 'price', 0.0)
            # print(type(base_price),"-----------")
            # electrician_charge = 100.0  # or dynamic
            # total_amount = float(base_price) + electrician_charge

            booking.action = 'approve'
            booking.job_started_at = timezone.now()
            # booking.quatation_amt = total_amount
            booking.save()

            return Response({
                "status": 200,
                "message": f"Quotation approved. Job has officially started.",
                # "quotation_amount": total_amount,
                "job_started_at": booking.job_started_at
            })

        else:  # Rejected
            booking.action = 'reject'
            booking.save()

            return Response({
                "status": 200,
                "message": "We understand the quotation was not approved. No worries – you may reschedule or contact us for further support.",
                "action": "Quotation rejected"
            })


class JobCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, booking_id):
        user = request.user

        try:
            booking = ServiceBook.objects.get(id=booking_id, assigned_technician=user)
        except ServiceBook.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Booking not found or unauthorized"
            }, status=404)

        # Set job start time if not already set
        if not booking.job_started_at:
            booking.job_started_at = timezone.now()

        # Mark status as complete
        booking.status = 'complete'

        # Optional comment and photo
        comment = request.data.get('comment')
        photo = request.FILES.get('photo')

        if comment:
            booking.comment = comment

        if photo:
            booking.photo = photo

        booking.save()

        return Response({
            "status": 200,
            "message": "Job marked as complete.",
            "data": {
                "booking_id": booking.id,
                "status": booking.status,
                "job_started_at": booking.job_started_at,
                "comment": comment or "No comment provided",
                "photo_uploaded": bool(photo)
            }
        }) 

class DownloadPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        user = request.user

        try:
            booking = ServiceBook.objects.get(id=booking_id, user=user)
        except ServiceBook.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Booking not found or access denied"
            }, status=status.HTTP_404_NOT_FOUND)

        if not booking.pdf_url:
            return Response({
                "status": 400,
                "message": "PDF not generated for this booking"
            }, status=status.HTTP_400_BAD_REQUEST)

        pdf_path = os.path.join(settings.MEDIA_ROOT, booking.pdf_url)

        if not os.path.exists(pdf_path):
            return Response({
                "status": 404,
                "message": "PDF file not found"
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf', filename=os.path.basename(pdf_path))


class PastOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        past_orders = ServiceBook.objects.filter(user=user, status__in=['complete', 'cancel']).order_by('-updated_date')

        serializer = ServiceBookSerializer(past_orders, many=True)
        return Response({
            "status": 200,
            "message": "Past bookings retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class ReBookingServiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            old_booking = ServiceBook.objects.get(id=booking_id, user=request.user)
        except ServiceBook.DoesNotExist:
            return Response({"status": 404, "message": "Booking not found."})

        # Create new booking with selected fields copied
        new_booking = ServiceBook.objects.create(
            user=old_booking.user,
            service=old_booking.service,
            technician_required=old_booking.technician_required,
            assigned_technician=old_booking.assigned_technician,
            quatation_amt=old_booking.quatation_amt,
            otp_required=old_booking.otp_required,
            action=old_booking.action,
            status='assign',  # reset status
            is_repeated=False,
            otp_generated_at=timezone.now(),
            service_start_otp=str(random.randint(100000, 999999))  # generate new OTP
        )
        #Mark old booking as repeated
        old_booking.is_repeated = True
        old_booking.save(update_fields=["is_repeated"])
        return Response({
            "status": 201,
            "message": "Re-order successful. New booking created.",
            "new_booking_id": new_booking.id
        })