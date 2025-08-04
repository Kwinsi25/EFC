from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import *
from django.shortcuts import get_object_or_404

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
    
  