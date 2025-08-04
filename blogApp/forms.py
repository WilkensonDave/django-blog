from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Comment, Profile


class CommentForm(forms.ModelForm):
    comment = models.TextField(max_length=400)
    
    class Meta:
        model = Comment
        exclude = ["post", "user"]
        
        labels ={
            "comment": "Your Comment"
        }
    

class  ProfileForm(forms.ModelForm):
    profile = models.TextField(max_length=400)
    
    class Meta:
        model = Profile
        exclude = ["user", "avatar"]
        
        labels={
            "bio": "Enter Bio"
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        
    
    
    


    

    
