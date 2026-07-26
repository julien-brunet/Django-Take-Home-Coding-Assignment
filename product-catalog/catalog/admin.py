from django.contrib import admin
from .models import Category, Product, Tag
from django.db.models import Count

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "tag_list"]
    list_filter = ["category", "tags"]
    search_fields = ["name", "description"]
    filter_horizontal = ["tags"]
    list_select_related = ["category"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    @admin.display(description="Tags")
    def tag_list(self, obj):
        return ", ".join(t.name for t in obj.tags.all()) or "—"
    