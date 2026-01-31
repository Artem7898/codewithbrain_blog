from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Category, Comment
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views', 'published_at', 'image_preview', 'image_source_display']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    #raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'category')}),
        ('Контент', {'fields': ('excerpt', 'content', 'tags')}),
        ('Изображение (используйте ОДИН из вариантов)', {
            'fields': ('featured_image', 'featured_image_url', 'image_preview_field'),
            'description': '''
            <div style="background: #f0f9ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>Инструкция:</strong><br>
            • <strong>Вариант 1:</strong> Загрузите изображение с компьютера<br>
            • <strong>Вариант 2:</strong> Вставьте ссылку на изображение из Sora/интернета<br>
            • <strong>Приоритет:</strong> Если заполнены оба поля, будет использоваться ссылка
            </div>
            '''
        }),
        ('Публикация', {'fields': ('status', 'published_at')}),
    )
    
    readonly_fields = ['image_preview_field']
    
    # Превью изображения в списке статей
    def image_preview(self, obj):
        if obj.get_featured_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px; object-fit: cover;" />', 
                obj.get_featured_image
            )
        return "🖼️"
    image_preview.short_description = 'Изобр.'
    
    # Отображение источника изображения
    def image_source_display(self, obj):
        if obj.featured_image_url:
            return format_html('<span style="color: green;">🌐 Ссылка</span>')
        elif obj.featured_image:
            return format_html('<span style="color: blue;">💾 Файл</span>')
        return "—"
    image_source_display.short_description = 'Источник'
    
    # Превью в форме редактирования
    def image_preview_field(self, obj):
        if obj.get_featured_image:
            return format_html(
                '''
                <div style="margin-top: 10px; padding: 15px; background: #1a1a1a; border-radius: 8px;">
                    <strong style="color: #fff;">Предпросмотр изображения:</strong><br>
                    <img src="{}" style="max-height: 300px; max-width: 100%; margin-top: 10px; border-radius: 8px;" />
                    <div style="margin-top: 10px; color: #888; font-size: 12px;">
                        {} • Приоритет: {}
                    </div>
                </div>
                ''', 
                obj.get_featured_image,
                obj.image_source,
                "Ссылка" if obj.featured_image_url else "Загруженный файл"
            )
        return format_html(
            '<div style="padding: 15px; background: #2a2a2a; border-radius: 8px; color: #888;">'
            'Изображение не загружено. Добавьте изображение или ссылку выше.'
            '</div>'
        )
    image_preview_field.short_description = 'Превью изображения'


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['author_name', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author_name', 'content']
    actions = ['approve_comments']
    
    @admin.action(description='Одобрить выбранные комментарии')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
