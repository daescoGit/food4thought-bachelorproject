from rest_framework import serializers
from .models import Comment, Quote, Vote

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment    
        fields = ['pk', 'user', 'post', 'body', 'date_created', 'is_quote', 'private']

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote  
        fields = ['quoter', 'quotee']

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote  
        fields = ['user', 'post', 'vote']