from math import ceil

from django.shortcuts import render, redirect

from .models import Post
from post.helper import page_cache
from post.helper import read_count
from post.helper import get_top_n


# Create your views here.


def post_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        post = Post.objects.create(title=title, content=content)
        return redirect('/post/read/?post_id=%s' % post.id)
    else:
        return render(request, 'create_post.html')


@read_count
@page_cache(10)
def post_read(request):
    post_id = int(request.GET.get('post_id'))
    post = Post.objects.get(id=post_id)
    return render(request, 'post_read.html', {'post': post})


@page_cache(10)
def post_list(request):
    page = int(request.GET.get('page', 1))
    per_page = 10
    total = Post.objects.count()
    pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    posts = Post.objects.all().order_by('-id')[start:end]
    return render(request, 'post_list.html', {'posts': posts, 'pages': range(pages)})


def post_edit(request):
    if request.method == "POST":
        post_id = int(request.POST.get('post_id'))
        post = Post.objects.get(id=post_id)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        return redirect('/post/read/?post_id={}'.format(post_id))
    else:
        post_id = int(request.GET.get('post_id'))
        post = Post.objects.get(id=post_id)
        return render(request, 'post_edit.html', {'post': post})


def post_search(request):
    keyword = request.POST.get('keyword')
    posts = Post.objects.filter(content__contains=keyword)
    return render(request, 'post_search.html', {'posts': posts})


def post_top(request):
    rank_data = get_top_n(10)
    return render(request, 'post_top.html', {'rank_data': rank_data})
