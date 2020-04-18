from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

# for collect expert subject.
class Subject(models.Model):
    subject_name = models.TextField(max_length=200, blank=True)     # collect expert subject.
    subject_keyword = models.TextField(max_length=200, blank=True)  # collect expert subject that was made into lowercase and remove space. it is used for searching.
    def __str__(self):
        return self.subject_name

# for collect name of receiver, name of person who send request and message for introduce.
class RequestSend(models.Model):
    sender = models.TextField(max_length=200,blank=True)            # collect request sender (student).
    request_message = models.TextField(max_length=600,blank=True)   # collect introduction message of request sender.
    receiver = models.TextField(max_length=200,blank=True)          # collect request receiver (tutor).
    def __str__(self):
        return self.sender

# for collect pair of student and tutor.
class MatchedName(models.Model):
    myself = models.TextField(max_length=200,blank=True)            # collect user
    match = models.TextField(max_length=200,blank=True)             # collect his partner
    def __str__(self):
        return self.match

# for collect user information.
class Userinfo(models.Model):
    name = models.TextField(max_length=200, blank=True)         # collect user name.
    first_name = models.TextField(max_length=200, blank=True)     # collect user first name.
    last_name = models.TextField(max_length=200, blank=True)     # collect user last name.
    age = models.TextField(max_length=10,blank=True)            # collect user age.
    school = models.TextField(max_length=200,blank=True)        # collect user school name.
    school_keyword = models.TextField(max_length=200,blank=True)     # collect user school that was made into uppercase and remove space. it is used for searching.
    gender = models.TextField(blank=True)                          # collect user gender.
    fb_link = models.TextField(null=True)                       # collect user Facebook profile link.
    expert_subject = models.ManyToManyField(Subject, related_name='Userinfos',blank=True)       # collect subject info.
    request = models.ManyToManyField(RequestSend,blank=True)    # collect request info.
    match = models.ManyToManyField(MatchedName,blank=True)      # collect match info.
    match_request = models.IntegerField(default=0)              # collect amount of student requests. it is used for notification.
    massage_list = models.IntegerField(default=0)               # collect amount of message. it is used for notification.

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
    post = models.ForeignKey(Userinfo,on_delete=models.CASCADE,related_name='comments',null=True)   # collect user info that receive comment.
    name = models.CharField(max_length=80,null=True)        # collect user info that send comment.
    comment = models.CharField(max_length=500,null=True)    # collect comment text.
    star = models.CharField(max_length=500,null=True)       # collect score.
    created_on = models.DateTimeField(auto_now_add=True,null=True)      # collect comment time.
    active = models.BooleanField(default=True,null=True)    # collect permission of comment.

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment to {} by {}'.format(self.post, self.name)

# for collect user information. used when signup.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)       # collect user first name.
    last_name = models.CharField(max_length=100, blank=True)        # collect user last name.
    college = models.CharField(max_length=100, blank=True)          # collect user college name
    email = models.EmailField(max_length=150)                       # collect user E-mail.
    age = models.TextField(max_length=10, blank=True)               # collect user age.
    gender = models.TextField()                                        # collect uesr gender.

    def __str__(self):
        return self.user.username

# for collect profile picture.
class Profilepic(models.Model):
    user = models.OneToOneField(Userinfo, on_delete=models.CASCADE)
    images = models.ImageField(default='default.png',upload_to='media')     # collect profile picture


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
