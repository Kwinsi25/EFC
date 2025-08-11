from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .models import Category
from .serializers import *
from django.shortcuts import get_object_or_404
from django.db.models import Q,Avg
from Accounts.auth_utils import get_authenticated_admin
from rest_framework.permissions import IsAuthenticated


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]  #Require JWT-authenticated user

    def get(self, request):
        categories = Category.objects.all().order_by('-created_date')
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response({"status": 200, "message": "Categories fetched", "data": serializer.data})

    def post(self, request):
        # Allow only if admin
        if not isinstance(request.user, CustomerProfile) or request.user.role != 'admin':
            return Response({
                "detail": "Unauthorized: Admin access required"
            }, status=401)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 201, "message": "Category created", "data": serializer.data})
        return Response({"status": 400, "message": "Validation failed", "errors": serializer.errors})


class CategoryDetailView(APIView):
    """
    GET: Retrieve a category by ID
    PATCH: Update category name
    DELETE: Delete a category
    """
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, context={'request': request})
        return Response({"status": 200, "message": "Category retrieved", "data": serializer.data})

    def patch(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "message": "Category updated", "data": serializer.data})
        return Response({"status": 400, "message": "Update failed", "errors": serializer.errors})

    def delete(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response({"status": 200, "message": "Category deleted", "data": {}})


class SubCategoryListCreateView(APIView):
    """
    GET: List all subcategories (services)
    POST: Create a new subcategory (service)
    """
    def get(self, request):
        subcategories = SubCategory.objects.all().order_by('-created_date')
        serializer = SubCategorySerializer(subcategories, many=True, context={'request': request})
        return Response({
            "status": 200,
            "message": "Subcategories fetched successfully",
            "data": serializer.data
        })

    def post(self, request):
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 201,
                "message": "Subcategory created successfully",
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "message": "Validation failed",
            "errors": serializer.errors
        })
    

class SubCategoryDetailView(APIView):
    """
    GET: Get subcategory by ID
    PATCH: Update subcategory
    DELETE: Delete subcategory
    """
    def get(self, request, subcategory_id):
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        serializer = SubCategorySerializer(subcategory, context={'request': request})
        return Response({
            "status": 200,
            "message": "Subcategory retrieved",
            "data": serializer.data
        })

    def patch(self, request, subcategory_id):
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        serializer = SubCategorySerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "message": "Subcategory updated",
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "message": "Update failed",
            "errors": serializer.errors
        })

    def delete(self, request, subcategory_id):
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        subcategory.delete()
        return Response({
            "status": 200,
            "message": "Subcategory deleted",
            "data": {}
        })
    
class StepListCreateView(APIView):
    """
    GET: List all steps
    POST: Create a new step
    """
    def get(self, request):
        steps = Step.objects.all().order_by('step_number')
        serializer = StepSerializer(steps, many=True)
        return Response({
            "status": 200,
            "message": "Steps fetched successfully",
            "data": serializer.data
        })

    def post(self, request):
        serializer = StepSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 201,
                "message": "Step created successfully",
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "message": "Validation failed",
            "errors": serializer.errors
        })
        

class StepDetailView(APIView):
    """
    GET: Get step by ID
    PATCH: Update a step
    DELETE: Delete a step
    """
    def get(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        serializer = StepSerializer(step)
        return Response({
            "status": 200,
            "message": "Step retrieved",
            "data": serializer.data
        })

    def patch(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        serializer = StepSerializer(step, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "message": "Step updated",
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "message": "Update failed",
            "errors": serializer.errors
        })

    def delete(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        step.delete()
        return Response({
            "status": 200,
            "message": "Step deleted",
            "data": {}
        })
    
class SubCategorySearchView(APIView):
    """
    Search sub-categories (services) based on keyword in name or description.
    """

    def get(self, request):
        keyword = request.query_params.get("search", "").strip()

        if keyword:
            services = SubCategory.objects.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword)
            )

            if services.exists():
                serializer = SubCategorySerializer(services, many=True, context={'request': request})
                return Response({
                    "status": 200,
                    "message": "Search result fetched successfully",
                    "data": serializer.data
                }, status=200)
            else:
                return Response({
                    "status": 404,
                    "message": f"No services found for keyword: '{keyword}'",
                    "data": []
                }, status=404)
        else:
            return Response({
                "status": 400,
                "message": "Please provide a keyword using ?search=your_keyword",
                "data": []
            }, status=400)
        
class ServiceCardListView(APIView):
    """
    API to fetch summarized service cards including:
    - Title
    - Price
    - Short Description
    - Average Rating & Review Count
    """

    def get(self, request):
        services = SubCategory.objects.all()
        if not services.exists():
            return Response({
                "status": 404,
                "message": "No services available",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceCardSerializer(services, many=True, context={'request': request})

        return Response({
            "status": 200,
            "message": "Service cards fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class SubCategoryFullDetailView(APIView):
    def get(self, request, subcategory_id):
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Service not found",
                "data": {}
            }, status=404)

        # Fetch steps
        steps = Step.objects.filter(service=subcategory).order_by('step_number')
        steps_data = StepSerializer(steps, many=True).data

        # Fetch approved reviews
        reviews = ReviewRating.objects.filter(service=subcategory, is_approved=True)
        reviews_data = ReviewRatingSerializer(reviews, many=True).data
        avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        review_count = reviews.count()

        response_data = {
            "id": subcategory.id,
            "title": subcategory.name,
            "description": subcategory.description,
            "cover_image": request.build_absolute_uri(subcategory.cover_image.url) if subcategory.cover_image else None,
            "price": subcategory.price,
            "steps": steps_data,
            "average_rating": round(avg_rating, 1),
            "total_reviews": review_count,
            "reviews": reviews_data
        }

        return Response({
            "status": 200,
            "message": "Service detail fetched successfully",
            "data": response_data
        }, status=200)
    
class ElectricianAfterServicePhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        electrician = request.user

        booking_id = request.data.get('booking')
        if not booking_id:
            return Response({"message": "Booking ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = ServiceBook.objects.get(id=booking_id)
            print(booking.user,"--------")
        except ServiceBook.DoesNotExist:
            return Response({"message": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        if booking.assigned_technician != electrician:
            return Response({"message": "You are not assigned to this booking."}, status=status.HTTP_403_FORBIDDEN)

        # Merge data with request.FILES (handled automatically by request.data)
        data = request.data.dict()
        data['electrician'] = electrician.id
        data['user'] = booking.user.id
        data['service'] = booking.service.id
        data['booking'] = booking.id

        serializer = ReviewCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                user=booking.user,
                electrician=electrician,
                service=booking.service,
                booking=booking
            )
            return Response({
                "status": 201,
                "message": "Image uploaded successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": 400,
                "message": "Invalid data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
class UserReviewElectricianView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        booking_id = request.data.get('booking')
        if not booking_id:
            return Response({"message": "Booking ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = ServiceBook.objects.get(id=booking_id, user=user)
        except ServiceBook.DoesNotExist:
            return Response({"message": "Booking not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        if not booking.assigned_technician:
            return Response({"message": "No electrician assigned for this booking."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate serializer
        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=user,
                electrician=booking.assigned_technician,
                service=booking.service,
                booking=booking
            )
            return Response({
                "status": 201,
                "message": "Review submitted successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": 400,
            "message": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class AdminReviewRatingListView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admin users allowed

    def get(self, request):
        reviews = ReviewRating.objects.all().order_by('-created_date')
        serializer = ReviewRatingSerializerForAdmin(reviews, many=True)
        return Response({
            "status": 200,
            "message": "All reviews fetched",
            "data": serializer.data
        })

    def patch(self, request, pk):
        """
        Partially update a review to set is_approved True or False
        """
        try:
            review = ReviewRating.objects.get(pk=pk)
        except ReviewRating.DoesNotExist:
            return Response({"message": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        is_approved = request.data.get('is_approved')
        if is_approved is None:
            return Response({"message": "'is_approved' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        review.is_approved = bool(is_approved)
        review.save()
        serializer = ReviewRatingSerializerForAdmin(review)
        return Response({
            "status": 200,
            "message": "Review approval status updated",
            "data": serializer.data
        })