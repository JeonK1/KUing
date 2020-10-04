from django.urls import path
from .views import RoomList, index
urlpatterns = [
    path('', index),
    path("room_list/<int:building_index>/", RoomList.as_view(), name="room_list"),
]
