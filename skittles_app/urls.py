from django.contrib import admin
from django.urls import path
from scores import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('live/<int:game_id>/', views.live_game, name='live_game'),
    path('live/', views.live_game, name='start_live_game'),
    path('add-player/', views.add_player, name='add_player'),
]