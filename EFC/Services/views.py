from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import *
from django.shortcuts import get_object_or_404
from django.db.models import Q

class CategoryListCreateView(APIView):
    """
    GET: List all categories
    POST: Create a new category
    """
    def get(self, request):
        categories = Category.objects.all().order_by('-created_date')
        serializer = CategorySerializer(categories, many=True)
        return Response({"status": 200, "message": "Categories fetched", "data": serializer.data})

    def post(self, request):
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
        serializer = CategorySerializer(category)
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
        serializer = SubCategorySerializer(subcategories, many=True)
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
        serializer = SubCategorySerializer(subcategory)
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
                serializer = SubCategorySerializer(services, many=True)
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