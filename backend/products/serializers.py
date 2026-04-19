from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Category, Product, UserInteraction


class CategoryChildSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='category_id', read_only=True)
    parentSlug = serializers.SerializerMethodField()
    productCount = serializers.IntegerField(source='product_count', read_only=True)

    def get_parentSlug(self, obj: Category) -> str | None:
        return obj.parent.slug if obj.parent_id and obj.parent else None

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'parentSlug', 'productCount']


class CategorySerializer(CategoryChildSerializer):
    children = CategoryChildSerializer(many=True, read_only=True)
    productCount = serializers.SerializerMethodField()

    def get_productCount(self, obj: Category) -> int:
        direct_count = getattr(obj, 'product_count', 0)
        child_count = sum(getattr(child, 'product_count', 0) for child in obj.children.all())
        return direct_count + child_count

    class Meta(CategoryChildSerializer.Meta):
        fields = ['id', 'slug', 'name', 'parentSlug', 'productCount', 'children']


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    originalPrice = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    categoryName = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    subcategoryName = serializers.SerializerMethodField()
    rating = serializers.FloatField(source='average_rating')
    reviews = serializers.IntegerField(source='num_reviews')
    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    isNew = serializers.SerializerMethodField()
    isBestSeller = serializers.SerializerMethodField()
    isTrending = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    brandName = serializers.SerializerMethodField()
    stockQuantity = serializers.IntegerField(source='stock_quantity', read_only=True)

    def _get_image_objects(self, obj: Product) -> list:
        return list(obj.images.all())

    def _get_effective_price(self, obj: Product) -> int:
        effective_price = getattr(obj, 'effective_price', None)
        if effective_price is not None:
            return int(effective_price)
        return obj.sale_price if obj.sale_price is not None else obj.price

    def _is_recent_product(self, obj: Product) -> bool:
        return obj.created_at >= timezone.now() - timedelta(days=30)

    def _get_top_level_category(self, obj: Product) -> Category:
        return obj.category.parent if obj.category.parent_id and obj.category.parent else obj.category

    def get_id(self, obj: Product) -> str:
        return str(obj.product_id)

    def get_price(self, obj: Product) -> int:
        return self._get_effective_price(obj)

    def get_originalPrice(self, obj: Product) -> int | None:
        return obj.price if obj.sale_price is not None else None

    def get_image(self, obj: Product) -> str:
        images = self._get_image_objects(obj)
        primary = next((image for image in images if image.is_primary), None)
        if primary:
            return primary.image_url
        if images:
            return images[0].image_url
        return ''

    def get_images(self, obj: Product) -> list[str]:
        images = self._get_image_objects(obj)
        ordered = sorted(images, key=lambda image: (not image.is_primary, image.image_id))
        return [image.image_url for image in ordered]

    def get_category(self, obj: Product) -> str:
        return self._get_top_level_category(obj).slug

    def get_categoryName(self, obj: Product) -> str:
        return self._get_top_level_category(obj).name

    def get_subcategory(self, obj: Product) -> str:
        if obj.category.parent_id:
            return obj.category.slug
        return obj.category.slug

    def get_subcategoryName(self, obj: Product) -> str:
        return obj.category.name

    def get_colors(self, obj: Product) -> list[str]:
        colors: list[str] = []
        for variant in obj.variants.all():
            color = variant.variant_attributes.get('color')
            if color and color not in colors:
                colors.append(color)
        return colors or ['Mac dinh']

    def get_sizes(self, obj: Product) -> list[str]:
        sizes: list[str] = []
        for variant in obj.variants.all():
            size = variant.variant_attributes.get('size')
            if size and size not in sizes:
                sizes.append(size)
        return sizes or ['STD']

    def get_isNew(self, obj: Product) -> bool:
        return bool(obj.is_new) or self._is_recent_product(obj)

    def get_isBestSeller(self, obj: Product) -> bool:
        return obj.num_reviews >= 150

    def get_isTrending(self, obj: Product) -> bool:
        interaction_count = getattr(obj, 'interaction_count', None)
        if interaction_count is None:
            interaction_count = obj.interactions.count()
        return interaction_count >= 10

    def get_brandName(self, obj: Product) -> str | None:
        return obj.brand.name if obj.brand_id and obj.brand else None

    class Meta:
        model = Product
        fields = [
            'id',
            'slug',
            'name',
            'price',
            'originalPrice',
            'image',
            'images',
            'category',
            'categoryName',
            'subcategory',
            'subcategoryName',
            'rating',
            'reviews',
            'colors',
            'sizes',
            'description',
            'isNew',
            'isBestSeller',
            'isTrending',
            'createdAt',
            'brandName',
            'stockQuantity',
        ]


class UserProductEventSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    user_id = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        if user_id is not None:
            validated_data['user_id'] = user_id
        return super().create(validated_data)

    class Meta:
        model = UserInteraction
        fields = [
            'interaction_id',
            'user_id',
            'product_id',
            'interaction_type',
            'session_id',
            'search_query',
            'score',
            'timestamp',
        ]
        read_only_fields = ['interaction_id', 'timestamp']
