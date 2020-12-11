from django.contrib.auth.decorators import login_required
from .models import Comment, Vote, Post
from django.http import HttpResponse, JsonResponse
from .serializers import CommentSerializer, QuoteSerializer, VoteSerializer
from rest_framework.parsers import JSONParser
from rest_framework import generics, permissions

# class comment_detail(generics.ListCreateAPIView):
#     def get_serializer_class(self):
#         return CommentSerializer

#     def get_queryset(self):
#         if request.method == 'GET':
#             comments = Comment.objects.all()
#             serializer = CommentSerializer(comments, many=True)
#             return JsonResponse(serializer.data, safe=False)
#         print(self.request.user)
#         print('reeeeeeee')

def newComment(request, post_id):
    if request.method == 'POST':
        if request.user.is_authenticated:   
            data = JSONParser().parse(request)
            data['user'] = request.user.id
            data['post'] = post_id
            if data.get('quotee'):
                data["is_quote"] = True
            commentSerializer = CommentSerializer(data=data)
            if commentSerializer.is_valid():
                commentSerializer.save()
                if data.get('quotee'):
                    data['quoter'] = commentSerializer['pk'].value
                    quoteSerializer = QuoteSerializer(data=data)
                    if quoteSerializer.is_valid():
                        quoteSerializer.save()
                    return JsonResponse({"pk":commentSerializer['pk'].value}, status=200)
                return JsonResponse({"pk":commentSerializer['pk'].value}, status=200)
            return JsonResponse(commentSerializer.errors, status=400)
        return JsonResponse({'status':'false','message':'Not logged in'}, status=400)


def deleteComment(request, post_id):
    if request.method == 'DELETE':
        if request.user.is_authenticated:   
            data = JSONParser().parse(request)
            pk = data['pk']
            comment = Comment.objects.get(pk=pk, user=request.user, post=post_id) 
            comment.delete()
            return JsonResponse({'message': 'Comment was deleted successfully!'}, status=200)
    return JsonResponse({'message': 'Could not delete comment'}, status=400)



def votePost(request, post_id):
    if request.method == "POST":
        data = JSONParser().parse(request)
        if Vote.objects.filter(user=request.user, post=post_id).exists():
            vote = Vote.objects.get(user=request.user, post=post_id)
            vote.vote = int(data['vote'])
            vote.save()
            post = Post.objects.get(pk=post_id)
            count = -post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count()
            return JsonResponse({'message': 'vote updated', 'count':count}, status=200)
        else: 
            data['user'] = request.user.id
            data['post'] = post_id

            voteSerializer = VoteSerializer(data=data)
            if voteSerializer.is_valid():
                voteSerializer.save()
                post = Post.objects.get(pk=post_id)
                count = -post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count()        
                return JsonResponse({'message': 'vote successful', 'count':count}, status=200)
            return JsonResponse(voteSerializer.errors, status=400)

    if request.method == "DELETE":
        if Vote.objects.filter(user=request.user, post=post_id).exists():
            vote = Vote.objects.get(user=request.user, post=post_id)
            vote.delete()
            post = Post.objects.get(pk=post_id)
            count = -post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count()
            return JsonResponse({'message': 'vote deleted', 'count': count}, status=200)
        return JsonResponse({'message': 'vote does not exist'}, status=400)




