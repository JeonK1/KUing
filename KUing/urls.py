from django.contrib import admin
from django.urls import path, include
from time_table.views import init, delete, index, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("time_table.urls")),

    # DB 수정용!!! 이유 없이 접근하지 않기
    path('init/', init),
    path('delete/', delete),

    # TODO: 추후에 다른 APP으로 이동시키기.
    path('login/', login),
]
