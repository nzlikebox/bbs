import time

from django.core.cache import cache
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class BlackListMiddleware(MiddlewareMixin):

    def process_request(self, request):
        user_ip = request.META['REMOTE_ADDR']
        print(user_ip)
        request_key = 'RequestIP_%s' % user_ip
        black_key = 'BlackIP_%s' % user_ip

        if cache.get(black_key):
            return render(request, 'black_list.html')

        now = time.time()
        t0, t1, t2 = cache.get(request_key, [0, 0, 0])
        if (now - t0) < 1:
            cache.set(black_key, 1, 15)
        else:
            cache.set(request_key, [t1, t2, now])
