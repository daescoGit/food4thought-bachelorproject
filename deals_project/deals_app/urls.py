from django.urls import path, include
from . import views
from .views import Base
from .api import newComment, deleteComment, votePost, getAddress


app_name = 'deals_app'

urlpatterns = [
    path('', Base.as_view(), name='base'),
    path('browse/<slug:base>/', Base.as_view(), name='base'),
    path('browse/<slug:base>/<slug:order>/', Base.as_view(), name='base'),
    path('browse/<slug:base>/<slug:order>/<int:page>/', Base.as_view(), name='base'),
    path('browse/<slug:base>/<slug:order>/<int:page>/<int:location>/', Base.as_view(), name='base'),
    path('post/<slug:slug>', views.post, name='post'),
    path('add', views.addPost, name='addPost'),
    path('post/<int:post_id>/vote', votePost, name='votePost'),
    path('post/<int:post_id>/comment', newComment, name='newComment'),
    path('get_address/', getAddress, name='getAddress'),
    path('post/<slug:slug>/get_address/', getAddress, name='getAddress'),
    path('post/<int:post_id>/comment/delete', deleteComment, name='deleteComment'),
    path('post/<slug:slug>/delete', views.delete, name='delete'),
    path('post/<slug:slug>/edit', views.edit, name='edit')
]