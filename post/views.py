from math import ceil

from django.shortcuts import render, redirect

from .models import Post
from .models import Comment
from .models import Tag
from .models import PostTagRelation
from post.helper import page_cache
from post.helper import read_count
from post.helper import get_top_n
from user.helper import login_required

# Create your views here.


@login_required
def post_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        uid = request.session.get('uid')
        post = Post.objects.create(title=title, content=content, uid=uid)
        return redirect('/post/read/?post_id=%s' % post.id)
    else:
        return render(request, 'post_create.html')


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


@login_required
def post_edit(request):
    if request.method == "POST":
        post_id = int(request.POST.get('post_id'))
        post = Post.objects.get(id=post_id)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        str_tags = request.POST.get('tags')
        tag_names1 = [x.strip() for x in str_tags.title().replace('，', ',').split(',') if x.strip()]
        tag_names2 = []
        for i in tag_names1:
            tag_names2 += i.split(' ')
        post.update_tags(tag_names2)
        return redirect('/post/read/?post_id={}'.format(post_id))
    else:
        post_id = int(request.GET.get('post_id'))
        post = Post.objects.get(id=post_id)
        relations = PostTagRelation.objects.filter(post_id=post_id).only('tag_id')
        tag_id_list = [t.tag_id for t in relations]
        tag_names_obj = Tag.objects.filter(id__in=tag_id_list)
        tag_names_list = [t.name for t in tag_names_obj]
        tags = ','.join(tag_names_list)
        return render(request, 'post_edit.html', {'post': post, 'tags': tags})


def post_search(request):
    keyword = request.POST.get('keyword')
    posts = Post.objects.filter(content__contains=keyword)
    return render(request, 'post_search.html', {'posts': posts})


def post_top(request):
    rank_data = get_top_n(10)
    return render(request, 'post_top.html', {'rank_data': rank_data})


@login_required
def post_comment(request):
    # uid = request.session['uid']
    uid = request.session.get('uid')
    post_id = request.POST.get('post_id')
    content = request.POST.get('content')
    Comment.objects.create(uid=uid, post_id=post_id, content=content)
    return redirect('/post/read/?post_id=%s' % post_id)


def post_tag_filter(request):
    tag_id = int(request.GET.get('tag_id'))
    tag = Tag.objects.get(id=tag_id)
    return render(request, 'post_tag_filter.html', {'posts': tag.posts()})
