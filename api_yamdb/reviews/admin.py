from django.contrib import admin


from .models import Comment, Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'title', 'score')
    search_fields = ('title',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

admin.site.register(Review, ReviewAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'review')
    search_fields = ('review',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Comment)
