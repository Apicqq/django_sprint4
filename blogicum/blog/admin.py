from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db import models
from django.forms import Textarea

from blog.models import Category, Location, Post, Comment

admin.site.empty_value_display = 'Не задано'


class PostInLine(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInLine,
    )
    list_display = (
        'title',
        'description',
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
    }
    list_display = (
        'is_published',
        'author',
        'category',
        'title',
        'location',
        'text',
        'pub_date',
    )
    list_editable = (
        'category',
        'text',
        'is_published',
    )
    search_fields = ('title', 'text', 'category')
    list_filter = ('category',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'text',
        'post',
        'created_at'
    )


class AdminUser(BaseUserAdmin):
    list_display = ('username', 'email', 'password', 'is_staff',
                    'posts_count',)
    search_fields = ('email',)
    ordering = ('username',)
    list_display_links = ('username',)

    @admin.display(description='Кол-во постов у пользователя')
    def posts_count(self, obj):
        return obj.posts.count()


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(Location)
admin.site.register(User, AdminUser)
