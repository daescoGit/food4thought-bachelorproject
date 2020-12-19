from django.shortcuts import render, get_object_or_404, reverse, redirect
from profile_app.models import UserProfile
from .models import Post, Comment, PostImage, Category, Quote, Postcode
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .serializers import CommentSerializer
from django.core.serializers import serialize
from django.contrib import messages
from .forms import PostForm
from django.forms.models import model_to_dict
from django.views.generic import View
import json
import base64
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.db import models
from .utils.images import get_image_from_data_url
import string
from django.db.models import Count

# Create your views here.
def addPost(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():

            post = Post()

            postcodeExists = Postcode.objects.filter(code=form.cleaned_data['postcode_code'])
            if(postcodeExists.exists()):
                post.postcode = postcodeExists[0]

            else:            
                postcode = Postcode()
                postcode.code = form.cleaned_data['postcode_code']
                postcode.text = form.cleaned_data['postcode_text']
                postcode.save()
                post.postcode = postcode

            post.title = form.cleaned_data['title']
            post.description = form.cleaned_data['description']
            post.expiration_date = form.cleaned_data['expiration_date']
            post.lng = form.cleaned_data['lng']
            post.lat = form.cleaned_data['lat']
            post.address_line_1 = form.cleaned_data['address_line_1']
            post.address_line_2 = form.cleaned_data['address_line_2']
            category = get_object_or_404(Category, pk=form.cleaned_data['category'])
            post.category = category

            post.user = request.user  

            if request.POST.get('newImagesLength'):
                newImagesLength = request.POST.get('newImagesLength')

                if(int(newImagesLength) < 1 ):
                    messages.error(request,'Image required, cannot have zero images')
                    return redirect('deals_app:addPost')

                post.thumbnail = get_image_from_data_url(request.POST.get('newImages0'))[0]
                post.save()

                for file_num in range(0, int(newImagesLength)):

                    image = get_image_from_data_url(request.POST.get(f'newImages{file_num}'))[0]

                    PostImage.objects.create(
                        post=post,
                        image=image
                    )

            messages.success(request,'Post created' )
            return redirect('deals_app:post', slug=post.slug)
        print('somethign went wrong wit hform')
        return render(request, 'deals_app/add.html', {'form':form})
    return render(request, 'deals_app/add.html', {'form':form})


# def newest(request):
#     posts = Post.objects.all()
    
#     for post in posts:
#         post.voteCount = (-post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count())
#         if request.user.is_authenticated:
#             if post.voter.filter(user=request.user).exists():
#                 post.voteStatus = post.voter.get(user=request.user).vote
            
#     posts = reversed(sorted(posts, key=lambda a: a.date_created))

#     return render(request, 'deals_app/hottest.html', {'posts':posts})

# def hottest(request):
#     posts = Post.objects.all()
    
#     for post in posts:
#         post.voteCount = (-post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count())
#         if request.user.is_authenticated:
#             if post.voter.filter(user=request.user).exists():
#                 post.voteStatus = post.voter.get(user=request.user).vote
            
#     posts = reversed(sorted(posts, key=lambda a: a.voteCount))

#     return render(request, 'deals_app/hottest.html', {'posts':posts})

class Base(View):
    def get(self, request, base='all', order='newest', page=0, location=0, *args, **kwargs):

        filters = models.Q()

        if base == 'all':
            print(' ')

        if base == 'our-picks':
            filters &= models.Q(
                staff_picked=True,
            )

        if Category.objects.filter(slug=base).exists():
            category = Category.objects.get(slug=base)
            filters &= models.Q(
                category=category,
            )

        if order == 'expired':
            filters &= models.Q(
                frozen=True,
            )
        
        if location != 0:
            postcode = Postcode.objects.get(code=location)

            filters &= models.Q(
                postcode=postcode,
            )
            
        def order_by_popularity(order):
            return print(order)

        order_by_popularity(order)
        posts = Post.objects.filter(filters).order_by('-date_created')[(int(page) * 10): (int(page) + 10)].annotate(num_comments=Count('comments'))


        if order == 'newest':
            print('hh')


        for post in posts:
            if request.user.is_authenticated:
                if post.voter.filter(user=request.user).exists():
                    post.voteStatus = post.voter.get(user=request.user).vote
        # posts = reversed(sorted(posts, key=lambda a: a.voteCount))
        nextPage = page + 1
        previousPage = page - 1

        jsonPosts = serialize('json', posts)  # the fields needed for products
        category = base.replace("-", " ")
        category = string.capwords(category)

        postcodes = Postcode.objects.all()
        return render(request, 'deals_app/index.html', {'posts':posts, 'postcodes':postcodes, 'jsonPosts':jsonPosts, 'base':base, 'currentCategory':category, 'currentPage':page, 'currentLocation': location, 'order': order, 'nextPage': nextPage, 'previousPage': previousPage})
    

def post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.voteCount = (-post.voter.filter(vote=-1).count() + post.voter.filter(vote=1).count())
    if request.user.is_authenticated:
        if post.voter.filter(user=request.user).exists():
            post.voteStatus = post.voter.get(user=request.user).vote
    comments = Comment.objects.filter(post=post)
    postImages = PostImage.objects.filter(post=post)
    profile = UserProfile.objects.get(user=post.user)
    commentCount = comments.count()
    privateCommentCount = comments.filter(private=True).count()
    commentquotes = []
    # user = request.user
    # if user.is_authenticated:
    for comment in comments:
        comment_ = {'comment':Comment.objects.get(id=comment.id), 'quote':Quote.objects.filter(quoter=comment).first()}
        commentquotes.append(comment_)

    return render(request, 'deals_app/post.html', {'profileImage':profile.image, 'post': post, 'commentquotes':commentquotes, 'commentCount':commentCount, 'privateCommentCount':privateCommentCount ,'postImages':postImages})

@login_required
def delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    messages.success(request,'Post deleted')
    return HttpResponseRedirect(reverse('deals_app:base'))

@login_required
def edit(request, slug):

    formpost = get_object_or_404(Post, slug=slug)
    formpostcode = get_object_or_404(Postcode, id=formpost.postcode.id)

    dictpost = model_to_dict(formpost)
    dictpostcode = {"postcode_text": formpostcode.text, "postcode_code":formpostcode.code}
    dictpost.update(dictpostcode)
    
    form = PostForm(dictpost)
    if request.method == "POST":
        form = PostForm(request.POST)
        post = get_object_or_404(Post, slug=slug)
        if form.is_valid():
            postcodeExists = Postcode.objects.filter(code=form.cleaned_data['postcode_code'])

            if(postcodeExists.exists()):
                post.postcode = postcodeExists[0]
            else:            
                postcode = Postcode()
                postcode.code = form.cleaned_data['postcode_code']
                postcode.text = form.cleaned_data['postcode_text']
                postcode.save()
                post.postcode = postcode

            post.title = form.cleaned_data['title']
            post.description = form.cleaned_data['description']
            post.expiration_date = form.cleaned_data['expiration_date']
            post.lng = form.cleaned_data['lng']
            post.lat = form.cleaned_data['lat']
            category = get_object_or_404(Category, pk=form.cleaned_data['category'])
            post.category = category

            user = request.user 
            post.user = user

            if(int(request.POST.get('existingImagesLength')) == 0 and int(request.POST.get('newImagesLength')) == 0 ):
                messages.error(request,'Image required, cannot have zero images')
                return redirect('deals_app:edit', slug = slug)


            if request.POST.get('existingImagesLength'):
                existingImagesLength = request.POST.get('existingImagesLength')
                pkarray = []

                for file_num in range(0, int(existingImagesLength)):
                    pkarray.append(request.POST.get(f'existingImages{file_num}')) 
                    
                PostImage.objects.filter(post=post).exclude(id__in=pkarray).delete()
                
                if int(existingImagesLength) > 0:
                    thumbnailpk = request.POST.get(f'existingImages0')
                    thumbnail = get_object_or_404(PostImage, id=thumbnailpk)

                    post.thumbnail = thumbnail.image

            if request.POST.get('newImagesLength'):
                newImagesLength = request.POST.get('newImagesLength')

                print(request.POST.get(f'newImages0'))
                for file_num in range(0, int(newImagesLength)):

                    image = get_image_from_data_url(request.POST.get(f'newImages{file_num}'))[0]

                    PostImage.objects.create(
                        post=post,
                        image=image
                    )

                if int(existingImagesLength) == 0:
                    post.thumbnail = get_image_from_data_url(request.POST.get('newImages0'))[0]

            messages.success(request,'Post updated')

        if request.POST['confirmCollection']:
            post.frozen = True

        post.save()


        return redirect('deals_app:post', slug = post.slug)



    user = request.user
    post = get_object_or_404(Post, slug=slug)
    postImages = PostImage.objects.filter(post=post)

    if (post.user == user ):
        return render(request, 'deals_app/edit.html', {'post':post, 'postImages': postImages, 'form':form})

    return HttpResponseRedirect(reverse('deals_app:base'))

