from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post, User
from .service import get_paginator, get_posts


def index(request):
    post_list = get_posts(Post.objects.select_related("author", "category")).order_by(
        "-pub_date"
    )
    page_obj = get_paginator(request, post_list)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    posts = get_object_or_404(Post, id=post_id)
    if request.user != posts.author:
        posts = get_object_or_404(get_posts(Post.objects), id=post_id)
    comments = posts.comments.order_by("created_at")
    form = CommentForm()
    return render(
        request, "blog/detail.html", {"post": posts, "form": form, "comments": comments}
    )


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    post_list = get_posts(category.posts.select_related("author")).order_by("-pub_date")
    page_obj = get_paginator(request, post_list)
    context = {"category": category, "page_obj": page_obj}
    return render(request, "blog/category.html", context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", request.user)
    context = {"form": form}
    return render(request, "blog/create.html", context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    now = timezone.now()
    if user.is_authenticated:
        posts_list = (
            user.posts.annotate(comment_count=Count("comments"))
            .select_related("author")
            .order_by("-pub_date")
        )
    else:
        posts_list = (
            user.posts.filter(is_published=True, pub_date__lte=now)
            .annotate(comment_count=Count("comments"))
            .select_related("author")
            .order_by("-pub_date")
        )
    page_obj = get_paginator(request, posts_list)
    context = {"profile": user, "page_obj": page_obj}
    return render(request, "blog/profile.html", context)


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", request.user)
    return render(request, "blog/user.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id)
    form = PostForm(request.POST, files=request.FILES or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect("blog:post_detail", post_id)
    form = PostForm(instance=post)
    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id)
    if request.method == "POST":
        form = PostForm(request.POST or None, instance=post)
        post.delete()
        return redirect("blog:index")
    form = PostForm(instance=post)
    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect("blog:post_detail", post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id)
    form = CommentForm(instance=comment)
    context = {"form": form, "comment": comment}
    return render(request, "blog/comment.html", context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id)
    context = {"comment": comment}
    return render(request, "blog/comment.html", context)
