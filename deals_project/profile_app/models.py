from django.db import models
from deals_app.models import Post
from django.contrib.auth.models import User
from django.db.models.signals import post_save
     
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    summary = models.CharField(max_length=200, default="This is your summary! Write something about yourself!")
    image = models.ImageField(upload_to='images/profile/', default="images/profile/1.jpg")

    # Create your models here.

def create_profile(sender,**kwargs ):
    if kwargs['created']:
        user_profile=UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile,sender=User)

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriber', on_delete=models.CASCADE )
    subscribee = models.ForeignKey(User, related_name='subscribee', on_delete=models.CASCADE)

    class Meta:
        unique_together = [['subscriber', 'subscribee']]

    def __str__(self):
        return f"{self.subscriber}, {self.subscribee}"

class Subscription_Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    post = models.ForeignKey(Post, on_delete=models.CASCADE )

    class Meta:
        unique_together = [['user', 'post']]

    def __str__(self):
        return f"{self.user}, {self.post}"