from django.contrib import admin
from django.urls import path
from scores import views
from django.shortcuts import redirect

def redirect_to_live(request):
    return redirect('start_game')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('live/<int:game_id>/', views.live_game, name='live_game'),
    path('live/', views.live_game, name='start_live_game'),  # This should point to start_game
    path('add-player/', views.add_player, name='add_player'),
    path('start-game/', views.start_game, name='start_game'),  # Ensure this is correct
    path('', redirect_to_live, name='root'),
]