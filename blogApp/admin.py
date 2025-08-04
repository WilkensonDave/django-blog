from django.contrib import admin

from .models import User, Blog, Comment, Tag, Author, PasswordReset, Profile
# Register your models here.


class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title', )}
    list_filter = ("title", 'author', 'date', 'tags')
    list_display = ('title', 'author', 'date')
    

class CommentAdmin(admin.ModelAdmin):
    list_filter = ('user__first_name', 'user__last_name')
    list_display = ('user__first_name', 'user__last_name')
    
    def user_first_name(self, obj):
        return obj.user.first_name
    
    def user_last_name(self, obj):
        return obj.user.first_name
    
    user_first_name.short_description = 'First Name'
    user_last_name.short_description = "Last Name"


class AuthorAdmin(admin.ModelAdmin):
    list_filter = ("first_name", "last_name")
    list_display = ('first_name', "last_name")


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display = ('name', )



admin.site.register(Blog, BlogAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PasswordReset)
admin.site.register(Profile)