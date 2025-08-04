from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category-detail'),
    path('subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list-create'),
    path('subcategories/<int:subcategory_id>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),
    path('steps/', StepListCreateView.as_view(), name='step-list-create'),
    path('steps/<int:step_id>/', StepDetailView.as_view(), name='step-detail'),
    path("search/", SubCategorySearchView.as_view(), name="subcategory-search"),
]
