from django.contrib import admin
from .models import Category, Location, Post, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")
    search_fields = ("name",)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_published",
        "category",
        "author",
        "location",
        "text",
        'pub_date',
        "created_at",
    )
    list_filter = ("is_published", "author")
    search_fields = ("title", "text")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
