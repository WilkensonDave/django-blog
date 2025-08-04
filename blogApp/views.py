from django.shortcuts import render, redirect, get_object_or_404
from django.http import  HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import *
from .forms import CommentForm, ProfileForm, UserUpdateForm
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils import timezone
from django.dispatch import receiver


def homepage(request):
    all_posts = Blog.objects.all().order_by("-date")[:3]
    user = request.user
    return render(request, 'blogApp/index.html', {"posts":all_posts, "user":user})


# Create your views here.
def registerView(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists! Use a different one.')
            return render(request, 'blogApp/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Try a different one please")
            return render(request, 'blogApp/register.html')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
        
        if password != confirm_password:
            messages.error(request, "Passwords do no match")
            return render(request, 'blogApp/register.html')
        
        user = User.objects.create(
            username=username,
            first_name=first_name,
            email=email,
            password=make_password(password)
        )
             
        if user is not None:
            messages.success(request, 'You hav been successfully register! You can login now')
            return redirect('loginView')
        
        else:
            messages.error(request, "Sorry check if the data entered are correct.")
            return redirect("registerView")
    
    return render(request, 'blogApp/register.html')
        
 
 
def loginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("homepage")
        
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "blogApp/login.html")
            
    return render(request, 'blogApp/login.html')


def logoutView(request):
    logout(request)
    messages.success(request, "You have logged out....")
    return redirect("homepage")


@login_required
def all_posts(request):
    all_posts = Blog.objects.all().order_by("-date")
    user = request.user
    return render(request, 'blogApp/all-posts.html', {"all_posts": all_posts, "user":user})

def post_details(request, slug):
    requested_post = get_object_or_404(Blog, slug=slug)
    
    if request.method == "GET":
        context = {
            "post":requested_post,
            "post_tags": requested_post.tags.all()[:2],
            "comment_form": CommentForm(),
            "comments":requested_post.comments.select_related("user").order_by("-id")[:3]
        }
        return render(request, 'blogApp/post-details.html', context)
    
    else:
        form = CommentForm(request.POST)
        post = Blog.objects.get(slug=slug)
        
        if request.user.is_authenticated:
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.user = request.user
                comment.save()
                
                messages.success(request, "Comment posted")
                return redirect(reverse("post_details", args=[slug]))
        
        else:
            messages.success(request, "You need to login to submit a comment.")
            return redirect("loginView")

def edit_comment(request, pk):
    current_comment = get_object_or_404(Comment, id=pk)
    if request.user !=  current_comment.user and not request.user.is_superuser:
         return redirect('unauthorize')
    
    
    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=current_comment)
        if form.is_valid():
            form.save()
            return redirect('post_details', slug=current_comment.post.slug)
    
    else:
        form = CommentForm(instance=current_comment)

    return render(request, 'blogApp/edit-comment.html', {"forms": form})
    

def delete_comment(request, pk):
    comment_to_delete = get_object_or_404(Comment, id=pk)
    if request.user != comment_to_delete.user and not request.user.is_superuser:
        return redirect('unauthorize')

    if request.user.is_authenticated:
        comment_to_delete.delete()
        messages.success(request, "Comment has been successfully deleted.")
        return redirect('post_details', slug=comment_to_delete.post.slug)
    else:
        return redirect('unauthorize')
    
def unauthorize(request):
    return render(request, "blogApp/unauthorized.html")


def forgetPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
    
        try:
            user = User.objects.get(email=email)
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()
            password_reset_url = reverse('reset-password',
                                        kwargs={'reset_id': new_password_reset.reset_id})
            
            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"
            email_body = f"Reset your password using the link below:\n\n\n{full_password_reset_url}"
            email_message = EmailMessage(
                'reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )
            
            email_message.fail_silently = True
            email_message.send()
            return redirect('password-reset-send', reset_id=new_password_reset.reset_id)
        
        except User.DoesNotExist:
            messages.error(request, f"No user found with this email '{email}'")
            return redirect("forget-password")
        
    return render(request, 'blogApp/forgetpassword.html')


def passwordresetsend(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, "blogApp/reset-password-link.html")
    else:
        messages.error(request, "Invalid reset id")
        return redirect("forget-password")
    
    
def resetPasword(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            
            password_have_error = False
            
            if password != confirm_password:
                password_have_error = True
                messages.error(request, "passwords do not match.")
            
            if len(password) < 8:
                password_have_error = True
                messages.error(request, "password must be at least 8 characters long.")
            
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)
            
            if timezone.now() > expiration_time:
                password_have_error = True
                messages.error(request, "Sorry the Reset link has been expired.")
                password_reset_id.delete()
            
            if not password_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
                messages.success(request, "Your password has been successfully reset. Try to login now")
                return redirect("loginView")
            else:
                return redirect('reset-password', reset_id=reset_id)
        
    except PasswordReset.DoesNotExist:
        messages.error(request, "Invalid reset id")
        return redirect("forget-password")
    
    return render(request, 'blogApp/reset-password.html')


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile_form = ProfileForm(request.POST or None, instance=profile)
        user_form = UserUpdateForm(request.POST or None, instance=request.user)
        
        if user_form.is_valid() and profile_form.is_valid():
           user_form.save()
           profile_form.save()
           return redirect("homepage")
    
    else:
        try:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileForm(instance=profile)
        except:
            return HttpResponse("You have not create your profile yet.")
            
        context = {
            "user_form":user_form,
            "profile_form":profile_form,
        }
        
    return render(request, "blogApp/profile.html", context)

# @login_required
def readlater(request):
    if request.method == "GET":
        stored_posts = request.session.get("stored_posts")
        context = {}
        if stored_posts is None or len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False
            
        else:
            posts = Blog.objects.filter(id__in=stored_posts)[:10]
            context["posts"] = posts
            context["has_posts"] = True    
        return render(request, "blogApp/readlater.html", context)
    
    else:
        stored_posts = request.session.get("stored_posts")
        if stored_posts is None:
            stored_posts = []
            
        post_id = int(request.POST["post_id"])
        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)
        request.session["stored_posts"] = stored_posts
        return redirect(reverse("all-posts"))