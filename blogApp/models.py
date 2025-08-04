from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.contrib.auth.models import User
import uuid


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=400, blank=True)
    
    
    def full_name(self):
        return f"{self.user.first_name}"
    
    
    def __str__(self):
        return self.full_name()
    

class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    def full_name(self):
        return f"{self.first_name}, {self.last_name}"
    
    def __str__(self):
        return self.full_name()
    
    class Meta:
        verbose_name_plural = "Authors"


class Tag(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = "tags"

class Blog(models.Model):
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="blog-images")
    date  = models.DateField(auto_now=True)
    slug = models.SlugField(db_index=True, unique=True, default="", blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="blogs")
    content = models.TextField(validators=[MinLengthValidator(50)])
    excerpt =models.CharField(max_length=250)
    tags = models.ManyToManyField(Tag, related_name='blogs')
    
    
    def get_absolute_url(self):
        return reverse("blog-details", kwargs={'slug': self.slug})
    
    
    @property
    def author_short(self):
        try:
            first = self.author.first_name
            last = self.author.last_name
            return f"{last}.{first[0]}" if first and last else str(self.author)
        
        except:
            return self.author
        
        
    def __str__(self):
        return f"{self.title}"


class Comment(models.Model):
    comment = models.TextField(max_length=400)
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateField(auto_now_add=True)
    

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"