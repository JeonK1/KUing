from django.urls import path
from .views import RoomList, index, RoomFilter, Room, RoomReservation, Notice


urlpatterns = [
    path('', index),
    path("room_list/<int:building_index>/room_filter", RoomFilter.as_view(), name="room_list"),
    path("room_list/<int:building_index>/", RoomList.as_view(), name="room_list"),
    path("room_list/<int:building_index>/<str:floor>", Room.as_view(), name="room_list"),
    path("reservation/<int:building_index>/<str:floor>", RoomReservation.as_view(), name="reservation"),
    path("notice", Notice.as_view(), name="notice"),
]
