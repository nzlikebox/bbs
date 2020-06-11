from django.db import models

from user.models import User
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    uid = models.IntegerField()

    @property
    def auth(self):
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(id=self.uid)
        return self._auth

    def comments(self):       # 为什么没写@property在post_read.html中也能以post.comments这种形式调用
        return Comment.objects.filter(post_id=self.id).order_by('-id')

    # 返回跟本篇帖子有关的tag对象的方法
    def tags(self):
        relations = PostTagRelation.objects.filter(post_id=self.id).only('tag_id')
        tag_id_list = [r.tag_id for r in relations]
        return Tag.objects.filter(id__in=tag_id_list)

    def update_tags(self, tag_names):
        Tag.ensure_exist(tag_names)

        update_names = set(tag_names)
        exist_names = {t.name for t in self.tags()}

        need_create_names = update_names - exist_names
        PostTagRelation.add_post_tags(self.id, need_create_names)

        need_delete_names = exist_names - update_names
        PostTagRelation.del_post_tags(self.id, need_delete_names)


class Comment(models.Model):
    uid = models.IntegerField()
    post_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def auth(self):
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(id=self.uid)
            return self._auth


class Tag(models.Model):
    name = models.CharField(max_length=16, unique=True)

    # 将用户输入的标签存入tag数据库中的方法
    @classmethod
    def ensure_exist(cls, names):
        exist_names = {t.name for t in cls.objects.filter(name__in=names)}
        new_names = set(names) - exist_names
        new_tags = [cls(name=name) for name in new_names]
        cls.objects.bulk_create(new_tags)

    def posts(self):
        post_id_obj_list = PostTagRelation.objects.filter(tag_id=self.id).only('post_id')
        post_id_list = [p.post_id for p in post_id_obj_list]
        return Post.objects.filter(id__in=post_id_list)


class PostTagRelation(models.Model):
    post_id = models.IntegerField()
    tag_id = models.IntegerField()

    @classmethod
    def add_post_tags(cls, post_id, tag_names):
        tags = Tag.objects.filter(name__in=tag_names).only('id')
        new_relations = [cls(post_id=post_id, tag_id=t.id) for t in tags]
        cls.objects.bulk_create(new_relations)

    @classmethod
    def del_post_tags(cls, post_id, tag_names):
        tags = Tag.objects.filter(name__in=tag_names).only('id')
        tag_id_list = [t.id for t in tags]
        cls.objects.filter(post_id=post_id, tag_id__in=tag_id_list).delete()
