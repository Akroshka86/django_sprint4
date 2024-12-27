from django.contrib import admin

from .models import Category, Comment, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'author',
        'created_at',
        'location',
        'category'
    )
    list_editable = (
        'is_published',
        'text'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
