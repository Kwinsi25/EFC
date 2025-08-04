from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer
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
