from django.contrib import admin

from .models import Group, Post, Follow, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настраивает отображение моделей
    постов и групп в интерфейсе администратора.
    """

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


admin.site.register(Group)
admin.site.register(Follow)
admin.site.register(Comment)
