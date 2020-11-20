from django.urls import path
from . import views

app_name = 'profile_app'


urlpatterns = [
    path('<int:user_id>/profile', views.profile, name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('subscriptions', views.subscription_list),
    path('<int:user_id>/profile/subscribe', views.subscription_detail)
]