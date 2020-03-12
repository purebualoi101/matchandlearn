from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    college = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)
    age = forms.CharField(max_length=10)


    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'age',
'email', 'college', )



class CommentForm(forms.ModelForm):
    star_score= [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
        ]
    star = forms.CharField(label="Choose your score", widget=forms.Select(choices=star_score))
    class Meta:
        model = Comment
        fields = ('comment','star',)