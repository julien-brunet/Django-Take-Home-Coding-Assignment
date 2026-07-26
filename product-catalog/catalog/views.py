from django.shortcuts import render
from django.db.models import Q
from .models import Category, Product, Tag


def product_list(request):
    """Product listing with combinable search and filters.

    Query parameters:
        q         -- free-text search across name and description
        category  -- category slug
        tags      -- tag slug, repeatable (?tags=copper&tags=pvc)
        tag_mode  -- "all" (default, AND) or "any" (OR)
    """
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    tag_slugs = [s for s in request.GET.getlist("tags") if s.strip()]
    tag_mode = "any" if request.GET.get("tag_mode") == "any" else "all"

    products = Product.objects.select_related("category").prefetch_related("tags")

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if tag_slugs:
        if tag_mode == "any":
            # OR: product carries at least one of the selected tags.
            products = products.filter(tags__slug__in=tag_slugs)
        else:
            # AND: product carries every selected tag. Each chained filter
            # adds its own join, so the conditions apply to different rows
            # rather than collapsing into one impossible condition.
            for slug in tag_slugs:
                products = products.filter(tags__slug=slug)

    products = products.distinct()

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "selected_query": query,
        "selected_category": category_slug,
        "selected_tags": tag_slugs,
        "tag_mode": tag_mode,
        "result_count": products.count(),
    }
    return render(request, "catalog/product_list.html", context)
