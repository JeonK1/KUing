from django.urls import path
from .views import RoomList, index, RoomFilter
urlpatterns = [
    path('', index),
    path("room_list/<int:building_index>/room_filter", RoomFilter.as_view(), name="room_list"),
    path("room_list/<int:building_index>/", RoomList.as_view(), name="room_list"),
]