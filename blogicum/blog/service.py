from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone


def get_posts(post_objects):
    return post_objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(comment_count=Count('comments'))


def get_paginator(request, items, num=10):
    return Paginator(items, num).get_page(request.GET.get('page'))
