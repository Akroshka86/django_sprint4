from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post, User
from .service import paginate_content, fetch_posts


def index(request):
    posts = fetch_posts(Post.objects.select_related(
        "author", "category")).order_by("-pub_date")
    page = paginate_content(request, posts)
    return render(request, "blog/index.html", {"page_obj": page})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        post = get_object_or_404(fetch_posts(Post.objects), id=post_id)
    comments = post.comments.order_by("created_at")
    comment_form = CommentForm()
    return render(
        request,
        "blog/detsil.html",
        {"post": post, "form": comment_form, "comments": comments},
    )


def category_posts(request, slug):
    selected_category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = fetch_posts(selected_category.posts.select_related("author")).order_by(
        "-pub_date"
    )
    page = paginate_content(request, posts)
    return render(
        request,
        "blog/category.html",
        {"category": selected_category, "page_obj": page},
    )


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", request.user)
    return render(request, "blog/create.html", {"form": form})


def profile(request, username):
    user_instance = get_object_or_404(User, username=username)
    current_time = timezone.now()
    if user_instance.is_authenticated:
        posts = (
            user_instance.posts.annotate(comment_count=Count("comments"))
            .select_related("author")
            .order_by("-pub_date")
        )
    else:
        posts = (
            user_instance.posts.filter(is_published=True, pub_date__lte=current_time)
            .annotate(comment_count=Count("comments"))
            .select_related("author")
            .order_by("-pub_date")
        )
    page_obj = paginate_content(request, posts)
    return render(
        request, "blog/profile.html", {"profile": user_instance, "page_obj": page_obj}
    )


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", request.user)
    return render(request, "blog/user.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post_instance = get_object_or_404(Post, id=post_id)
    if request.user != post_instance.author:
        return redirect("blog:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post_instance
    )
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    return render(request, "blog/post_form.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post_instance = get_object_or_404(Post, id=post_id)
    if request.user != post_instance.author:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST or None, instance=post_instance)
        post_instance.delete()
        return redirect("blog:index")
    form = PostForm(instance=post_instance)
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post_instance = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post_instance
        comment.author = request.user
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment_instance = get_object_or_404(Comment, id=comment_id)
    if request.user != comment_instance.author:
        return redirect("blog:post_detail", post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment_instance)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    form = CommentForm(instance=comment_instance)
    return render(
        request, "blog/comment.html", {"form": form, "comment": comment_instance}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment_instance = get_object_or_404(Comment, id=comment_id)
    if request.user != comment_instance.author:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        comment_instance.delete()
        return redirect("blog:post_detailw", post_id=post_id)
    return render(request, "blog/comment.html", {"comment": comment_instance})
