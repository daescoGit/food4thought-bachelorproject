import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, JsonWebsocketConsumer
from channels.consumer import AsyncConsumer
from .models import Post, Comment, Quote
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import asyncio
from django.db.models import signals
from django.dispatch import receiver
import channels.layers
from django.core import serializers
from django.shortcuts import get_object_or_404

# this needs to:
# listen to new comments on posts (if OP)
# listen to new replies to own comments
# mark as read on click (front end)
# sync across instances 
# try-except db calls?

class NotificationConsumer(JsonWebsocketConsumer):

    def connect(self):

        personal_group = 'personal_group_'+str(self.scope["user"].id)
        async_to_sync(self.channel_layer.group_add)(personal_group, self.channel_name)
        payload = []

        # all unread comments from own post
        unread_from_OP = Comment.objects.exclude(user=self.scope["user"]).filter(post__user=self.scope["user"]).filter(read_by_author=False)

        for single_unread in unread_from_OP:
            payload.append(single_unread)

        # all unread replies from own comments
        unread_from_replies = Quote.objects.exclude(quoter__user=self.scope["user"]).filter(quotee__user=self.scope["user"]).filter(quotee__read_by_author=False)
        
        #put these in custom method probably & clean up   

        for quote_ref in unread_from_replies:
            single_unread = Comment.objects.get(id=quote_ref.quoter.id)
            payload.append(single_unread)

        serialized_payload = serializers.serialize('json', payload)
        
        # no need to use group for initial on-load payload
        # this part could be just via views too
        async_to_sync(self.channel_layer.send)(self.channel_name, {
            'type': 'events.alarm',
            'data': {
                'multi': True,
                'data': serialized_payload,
            }})
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'personal_group',
            self.channel_name
        )
        self.close()

    def receive_json(self, content, **kwargs):
        print(f"Received event: {content}")
        comment = Comment.objects.get(pk=content["pk"])
        comment.read_by_author = True
        comment.save()
        print(comment)

    def events_alarm(self, event):
        self.send_json(event['data'])

    @staticmethod # avoid requiring self arg for signal method
    @receiver(signals.post_save, sender=Comment)
    @receiver(signals.post_save, sender=Quote)
    def comment_signal(sender, instance, **kwargs):
        layer = channels.layers.get_channel_layer()

        # we cannot access self or request.user, so we need to examine the incoming comment and send accordingly
        # if comment on user's post // send to the group of comment-post-user
        # group is useful here for sync if user is connected on multiple devices
        if sender == Quote and instance.quoter.read_by_author == False and instance.quoter.user != instance.quotee.user:
            serialized_payload = serializers.serialize('json', [instance.quoter])
            async_to_sync(layer.group_send)('personal_group_'+str(instance.quotee.user.id), {
                'type': 'events.alarm',
                'data': {
                    'multi': False,
                    'data': serialized_payload
                }
            })
        if sender == Comment and instance.is_quote == False and instance.read_by_author == False and instance.user != instance.post.user:
            serialized_payload = serializers.serialize('json', [instance])
            async_to_sync(layer.group_send)('personal_group_'+str(instance.post.user.id), {
                'type': 'events.alarm',
                'data': {
                    'multi': False,
                    'data': serialized_payload
                }
            })
        # clean up into method?










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

# sync consumer

""" class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'xy',
                'message': message
            }
        )

    # Receive message from room group
    def xy(self, event):
        message = event['message'] #dbu #Comment.objects.count() # event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
 """