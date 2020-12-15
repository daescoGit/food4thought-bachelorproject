from django.contrib.auth.models import User
from django.db import models
from datetime import datetime    
from django.db.models.signals import pre_save, post_save, post_delete
import channels.layers
from asgiref.sync import async_to_sync
from django.dispatch import receiver
import json

from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("deals_app:post", kwargs={"slug": self.slug})

class Postcode(models.Model):
    code = models.IntegerField()
    region = models.CharField(max_length=200)

    def __str__(self):
        return self.code

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80, null=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200)
    postcode = models.ForeignKey(Postcode, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    new_price = models.IntegerField()
    old_price = models.IntegerField()
    vote_score = models.IntegerField(default=0)
    thumbnail = models.ImageField(upload_to='images/')
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    staff_picked = models.BooleanField(default=False)
    expiration_date = models.DateField()
    lng = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return self.title

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='voter')
    vote = models.IntegerField()

    class Meta:
        unique_together = [['user', 'post']]
        
    def __str__(self):
        return f"{self.user.username}, {self.post.title}"

class PostImage(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'images/')

    def __str__(self):
        return self.post.title

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    read_by_author = models.BooleanField(default=False)
    is_quote = models.BooleanField(default=False)
    private = models.BooleanField(default=False)

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.user)

class Quote(models.Model):
    quoter = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='quoter')
    quotee = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='quotee')

    class Meta:
        unique_together = [['quoter', 'quotee']]

    def __str__(self):
        return '{} is quoting {}'.format(self.quoter, self.quotee)


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_slug_receiver(sender, instance, *args, **kwargs):
    instance.slug = create_slug(instance)

pre_save.connect(pre_save_slug_receiver, sender=Post)

def update_post_votes(sender, instance, *args, **kwargs):

    post = Post.objects.get(id=instance.post.id)
    if post:
        post.vote_score = (-post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count())
        post.save(update_fields=['vote_score'])

post_save.connect(update_post_votes, sender=Vote)
post_delete.connect(update_post_votes, sender=Vote)

# for channels consumer
