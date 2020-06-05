from django.core.cache import cache
from common import rds
from .models import Post


def page_cache(timeout):
    def wrapper1(view_func):
        def wrapper2(request):
            key = 'page_cache_%s_%s' % (request.session.session_key, request.get_full_path())
            response = cache.get(key)
            print('get from cache', response)
            if response is None:
                response = view_func(request)
                print('get from view', response)
                cache.set(key, response, timeout)
                print('set cache for page')
            return response
        return wrapper2
    return wrapper1


def read_count(read_view):
    def wrapper(request):
        response = read_view(request)
        if response.status_code == 200:
            post_id = int(request.GET.get('post_id'))
            rds.zincrby('ReadRank', post_id)
        return response
    return wrapper


def get_top_n(num):
    ori_data = rds.zrevrange('ReadRank', 0, num - 1, withscores=True)
    cleaned_data = [[int(post_id), int(count)] for post_id, count in ori_data]

    post_id_list = [post_id for post_id, _ in cleaned_data]
    post_dict = Post.objects.in_bulk(post_id_list)
    for item in cleaned_data:
        item[0] = post_dict[item[0]]
    rank_data = cleaned_data
    return rank_data
