from django.contrib import admin
from .models import (
    Platform, Product, ProductVariant, ProductOffer, PriceHistory,
    Wishlist, URLAnalysis, Seller, Review, ReviewSummary, Coupon,
    DataSource, ComparisonSession, SearchHistory, AIAnalysis,
    AIProviderLog, AuditLog,
)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "website_url", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "brand", "created_at")
    list_filter = ("category", "brand")
    search_fields = ("title", "brand", "category")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "variant_name", "storage", "ram", "color", "is_default")
    list_filter = ("is_default",)
    search_fields = ("product__title", "variant_name")


@admin.register(ProductOffer)
class ProductOfferAdmin(admin.ModelAdmin):
    list_display = (
        "id", "product", "store_name", "platform", "current_price",
        "rating", "in_stock", "data_source", "data_status",
        "matching_confidence", "delivery_days",
    )
    list_filter = ("store_name", "platform", "in_stock", "data_source", "data_status")
    search_fields = ("product__title", "store_name", "platform__name")


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "store_name", "price", "currency", "collection_method", "recorded_at")
    list_filter = ("store_name", "currency", "collection_method")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "guest_id", "product", "added_at")


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "platform", "rating", "reliability_score", "is_verified")
    list_filter = ("platform", "is_verified")
    search_fields = ("name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "platform", "author_name", "rating", "verified_purchase", "data_status")
    list_filter = ("platform", "verified_purchase", "data_status")
    search_fields = ("product__title", "author_name")


@admin.register(ReviewSummary)
class ReviewSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "total_reviews", "average_rating", "review_confidence", "ai_provider")
    search_fields = ("product__title",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "platform", "discount_amount", "discount_percent", "is_active")
    list_filter = ("platform", "is_active")
    search_fields = ("code",)


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "source_type", "platform", "reliability_score", "is_active")
    list_filter = ("source_type", "is_active")


@admin.register(ComparisonSession)
class ComparisonSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "guest_id", "product", "created_at")
    list_filter = ("created_at",)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "guest_id", "query", "results_count", "created_at")
    search_fields = ("query",)


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "provider", "status", "analysis_type", "is_fallback", "created_at")
    list_filter = ("provider", "status", "analysis_type", "is_fallback")
    search_fields = ("product__title",)


@admin.register(AIProviderLog)
class AIProviderLogAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "status", "request_tokens", "response_tokens", "response_time_ms", "created_at")
    list_filter = ("provider", "status")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "model_name", "object_id", "created_at")
    list_filter = ("action", "model_name")
    search_fields = ("object_repr",)
