from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import BlogPost


def blog_index(request: HttpRequest) -> HttpResponse:
    posts = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)
    return render(request, "blog/blog_index.html", {"posts": posts})


def blog_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(BlogPost, slug=slug, status=BlogPost.Status.PUBLISHED)
    return render(request, "blog/blog_detail.html", {"post": post})
