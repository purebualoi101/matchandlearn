from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

# for collect expert subject.
class Subject(models.Model):
    name_subject = models.TextField(max_length=200, blank=True)
    subject_keyword = models.TextField(max_length=200, blank=True)
    def __str__(self):
        return self.name_subject

# for collect name of receiver, name of person who send request and message for introduce.
class RequestSend(models.Model):
    request_list = models.TextField(max_length=200,blank=True)
    request_message = models.TextField(max_length=600,blank=True)
    receiver = models.TextField(max_length=200,blank=True)
    def __str__(self):
        return self.request_list

# for collect pair of student and tutor.
class MatchedName(models.Model):
    match = models.TextField(max_length=200,blank=True)
    myself = models.TextField(max_length=200,blank=True)
    def __str__(self):
        return self.match

# for collect user information.
class Userinfo(models.Model):
    name = models.TextField(max_length=200, blank=True)
    fullname = models.TextField(max_length=200, blank=True)
    lastname = models.TextField(max_length=200, blank=True)
    age = models.TextField(max_length=10,blank=True)
    school = models.TextField(max_length=200,blank=True)
    schoolkey = models.TextField(max_length=200,blank=True)
    bio = models.TextField(blank=True)
    fb_link = models.TextField(null=True)
    expert_subject = models.ManyToManyField(Subject, related_name='Userinfos',blank=True)
    request = models.ManyToManyField(RequestSend,blank=True)
    match = models.ManyToManyField(MatchedName,blank=True)
    match_request = models.IntegerField(default=0)
    massage_list = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    # function for remove number of notification.
    def read(self):
        self.match_request = 0
        self.save()

    # function for +1 notification.
    def notify(self):
        self.match_request = self.match_request + 1
        self.save()

    # function for -1 notification.
    def denotify(self):
        self.match_request = self.match_request - 1
        self.save()

# for collect Commentator, comment text and score.
class Comment(models.Model):
    post = models.ForeignKey(Userinfo,on_delete=models.CASCADE,related_name='comments',null=True)
    name = models.CharField(max_length=80,null=True)
    comment = models.CharField(max_length=500,null=True)
    star = models.CharField(max_length=500,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    active = models.BooleanField(default=True,null=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment to {} by {}'.format(self.post, self.name)

# for collect user information. used when signup.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=150)
    age = models.TextField(max_length=10, blank=True)
    bio = models.TextField()

    def __str__(self):
        return self.user.username

# for collect profile picture.
class Profilepic(models.Model):
    user = models.OneToOneField(Userinfo, on_delete=models.CASCADE)
    images = models.ImageField(default='default.png',upload_to='media')


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
