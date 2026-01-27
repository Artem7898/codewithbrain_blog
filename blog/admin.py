from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Category, Comment


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views', 'published_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    #raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'category')}),
        ('Контент', {'fields': ('excerpt', 'content', 'featured_image', 'tags')}),
        ('Публикация', {'fields': ('status', 'published_at')}),
    )


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['author_name', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author_name', 'content']
    actions = ['approve_comments']
    
    @admin.action(description='Одобрить выбранные комментарии')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
