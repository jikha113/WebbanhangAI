from datetime import timedelta

from django.db.models import Count, Prefetch, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import generics

from .models import Category, Product, UserInteraction
from .serializers import CategorySerializer, ProductSerializer, UserProductEventSerializer


def _parse_int(raw: str | None) -> int | None:
    if raw in {None, ''}:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _parse_list_param(query_params, key: str) -> list[str]:
    values: list[str] = []
    for raw_value in query_params.getlist(key):
        for item in raw_value.split(','):
            value = item.strip()
            if value:
                values.append(value)
    return values


def _catalog_queryset():
    return (
        Product.objects.filter(is_active=True)
        .select_related('brand', 'category', 'category__parent')
        .prefetch_related('images', 'variants')
        .annotate(
            effective_price=Coalesce('sale_price', 'price'),
            interaction_count=Count('interactions', distinct=True),
        )
    )


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        child_queryset = (
            Category.objects.filter(parent__isnull=False)
            .select_related('parent')
            .annotate(product_count=Count('products', filter=Q(products__is_active=True), distinct=True))
            .order_by('name')
        )

        return (
            Category.objects.filter(parent__isnull=True)
            .annotate(product_count=Count('products', filter=Q(products__is_active=True), distinct=True))
            .prefetch_related(Prefetch('children', queryset=child_queryset))
            .order_by('name')
        )


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = _catalog_queryset()

        category = self.request.query_params.get('category')
        is_new = self.request.query_params.get('new')
        is_sale = self.request.query_params.get('sale')
        search = (self.request.query_params.get('search') or '').strip()
        subcategories = _parse_list_param(self.request.query_params, 'subcategory')
        min_price = _parse_int(self.request.query_params.get('min_price'))
        max_price = _parse_int(self.request.query_params.get('max_price'))
        sort = self.request.query_params.get('sort')

        if category:
            queryset = queryset.filter(Q(category__slug=category) | Q(category__parent__slug=category))
        if is_new in {'true', '1'}:
            recent_threshold = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(Q(is_new=True) | Q(created_at__gte=recent_threshold))
        if is_sale in {'true', '1'}:
            queryset = queryset.filter(sale_price__isnull=False)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(feature_text__icontains=search)
            )
        if subcategories:
            queryset = queryset.filter(category__slug__in=subcategories)
        if min_price is not None:
            queryset = queryset.filter(effective_price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(effective_price__lte=max_price)

        ordering_map = {
            'price_asc': ['effective_price', '-created_at'],
            'price_desc': ['-effective_price', '-created_at'],
            'newest': ['-created_at'],
            'oldest': ['created_at'],
        }
        ordering = ordering_map.get(sort, ['-created_at'])

        return queryset.order_by(*ordering)


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = _catalog_queryset()
    serializer_class = ProductSerializer
    lookup_field = 'product_id'
    lookup_url_kwarg = 'id'


class UserEventCreateAPIView(generics.CreateAPIView):
    queryset = UserInteraction.objects.all()
    serializer_class = UserProductEventSerializer
