from django.urls import path, include
from . import views
from .views import Base
from .api import newComment, deleteComment, votePost


app_name = 'deals_app'

urlpatterns = [
    path('', Base.as_view(), name='base'),
    path('<slug:base>/', Base.as_view(), name='base'),
    path('<slug:base>/<slug:order>/', Base.as_view(), name='base'),
    path('<slug:base>/<slug:order>/<int:page>/', Base.as_view(), name='base'),
    path('post/<slug:slug>', views.post, name='post'),
    path('add', views.addPost, name='addPost'),
    path('post/<int:post_id>/vote', votePost, name='votePost'),
    path('post/<int:post_id>/comment', newComment, name='newComment'),
    path('post/<int:post_id>/comment/delete', deleteComment, name='deleteComment'),
    path('post/<slug:slug>/delete', views.delete, name='delete'),
    path('post/<slug:slug>/edit', views.edit, name='edit')
]