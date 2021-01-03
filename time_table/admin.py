from django.contrib import admin
from .models import Lecture, LectureTime, Reservation

# admin.site.register(Lecture)
admin.site.register(LectureTime)

@admin.register(Lecture)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'building',]
    search_fields = ['title',]
    # list_display_links = ['id', 'title']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    pass