from math import ceil

from django.shortcuts import render, redirect

from .models import Post

# Create your views here.


def post_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        post = Post.objects.create(title=title, content=content)
        return redirect('/post/read/?post_id=%s' % post.id)
    else:
        return render(request, 'create_post.html')


def post_read(request):
    post_id = int(request.GET.get('post_id'))
    post = Post.objects.get(id=post_id)
    return render(request, 'read_post.html', {'post': post})


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
        return render(request, 'edit_post.html', {'post': post})


def post_search(request):
    keyword = request.POST.get('keyword')
    posts = Post.objects.filter(content__contains=keyword)
    return render(request, 'post_search.html', {'posts': posts})
