import json
import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from .models import Post, Comment, Quote
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.core import serializers


# todo: 
# expand to "my watched" (activity categories/posts/etc)
# try-except db calls?
# signal for updates on status=read (replace front end dummy system to keep integrity+sync devices)
# fix user ref from id to name
# (potential front end) reference post, date
# seperate into own app?
# delete signal for if a post get deleted

class NotificationConsumer(JsonWebsocketConsumer):

    def connect(self):
        personal_group = 'personal_group_'+str(self.scope["user"].id)
        async_to_sync(self.channel_layer.group_add)(personal_group, self.channel_name)
        payload = []

        def loop_handler(query_set, is_quote):
            for obj in query_set:
                if is_quote:
                    obj = obj.quoter
                data = {
                    "id": obj.id,
                    "body": obj.body,
                    "user": obj.user.username,
                    "is_quote": is_quote,
                    "slug": obj.post.slug
                }
                # comment may already be in payload from quotes
                if payload != []:
                    for item in payload:
                        if data["id"] == item["id"]:
                            continue
                        payload.append(data)
                else:
                    payload.append(data)

        # all unread replies from own comments
        unread_from_replies = Quote.objects.exclude(quoter__user=self.scope["user"]).filter(quotee__user=self.scope["user"]).filter(quoter__read_by_author=False).order_by('-quotee__date_created')
        loop_handler(unread_from_replies, True)

        # all unread comments from own post
        unread_from_OP = Comment.objects.exclude(user=self.scope["user"]).filter(post__user=self.scope["user"]).filter(read_by_author=False).order_by('-date_created')
        loop_handler(unread_from_OP, False)
        
        # no need to use group for initial on-load payload
        async_to_sync(self.channel_layer.send)(self.channel_name, {
            'type': 'events.alarm',
            'data': {
                'multi': True,
                'data': payload,
            }})
        self.accept()

    def disconnect(self, close_code):
        personal_group = 'personal_group_'+str(self.scope["user"].id)
        async_to_sync(self.channel_layer.group_discard)(
            personal_group,
            self.channel_name
        )
        self.close()

    def receive_json(self, content, **kwargs):
        print(f"Received event: {content}")
        comment = get_object_or_404(Comment, id=content["id"])
        print(comment)
        comment.read_by_author = True
        comment.save()

    def events_alarm(self, event):
        self.send_json(event['data'])

    @staticmethod # avoid requiring self arg for signal method
    @receiver(signals.post_save, sender=Comment)
    @receiver(signals.post_save, sender=Quote)
    #@receiver(signals.post_delete, sender=Comment)
    def comment_signal(sender, instance, **kwargs):
        layer = channels.layers.get_channel_layer()
        # we cannot access self or request.user, so we need to examine the incoming comment and send accordingly
        # if comment on user's post // send to the group of comment-post-user
        # group is useful here for sync if user is connected on multiple devices
        
        def typeHandler(post, target):
            payload = [{
                "id": post.id,
                "body": post.body,
                "user": post.user.username,
                "is_quote": post.is_quote,
                "slug": post.post.slug
            }]

            async_to_sync(layer.group_send)('personal_group_'+str(target), {
                'type': 'events.alarm',
                'data': {
                    'multi': False,
                    'data': payload
                }
            })

        if sender == Quote and instance.quoter.read_by_author == False and instance.quoter.user != instance.quotee.user:
            typeHandler(instance.quoter, instance.quotee.user.id)
        if sender == Comment and instance.is_quote == False and instance.read_by_author == False and instance.user != instance.post.user:
            typeHandler(instance, instance.post.user.id)

class LivePostConsumer(JsonWebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)('post_list_group', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'post_list_group',
            self.channel_name
        )
        self.close()

    def events_alarm(self, event):
        self.send_json(event['data'])

    @staticmethod
    @receiver(signals.post_save, sender=Post)
    #@receiver(signals.post_delete, sender=Comment)
    def comment_signal(sender, instance, **kwargs):
        layer = channels.layers.get_channel_layer()
        async_to_sync(layer.group_send)('post_list_group', {
            'type': 'events.alarm',
            'data': {
                "data": serializers.serialize("json", [instance]),
                'username': instance.user.username
            }
        })

# (NOT WORKING ATM)
# todo:
# broadcast/group
# hook up to user
# convert to async
class UserStatusConsumer(WebsocketConsumer):

    def connect(self):  
        #if self.scope["user"].is_anonymous:
        #if self.scope["user"].is_authenticated:
        # userPosts = Post.objects.filter(user__id=self.scope["user"].id)
        async_to_sync(self.channel_layer.group_add)("statusTracker", self.channel_name)
        # anyone con to socket get user list

        async_to_sync(self.channel_layer.group_send)(
            "statusTracker",
            {
                "type": "user.handler",
                "message": str(self.scope["user"].id),
            },
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("statusTracker", self.channel_name)

    # on recive data from client
    def receive(self, text_data):
        #self.send(text_data=self.scope["user"] + ": " + text_data)
        print(text_data)
        #text_data_json = json.loads(text_data)
        #message = text_data_json['message']

    def user_handler(self, event):
        print("e", event)
        self.send(event['message'])

class LiveCommentConsumer(WebsocketConsumer):
    pass