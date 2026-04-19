from django.urls import path

from .views import CategoryListAPIView, ProductDetailAPIView, ProductListAPIView, UserEventCreateAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('', ProductListAPIView.as_view(), name='product-list'),
    path('events/', UserEventCreateAPIView.as_view(), name='product-event-create'),
    path('<str:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
]
