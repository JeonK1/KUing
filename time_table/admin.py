from django.contrib import admin
from .models import Lecture, LectureTime

# admin.site.register(Lecture)
admin.site.register(LectureTime)

@admin.register(Lecture)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'building',]
    # list_display_links = ['id', 'title']