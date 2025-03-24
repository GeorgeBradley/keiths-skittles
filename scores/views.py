from django.shortcuts import render, redirect
from django.db.models import Sum, Max
from .models import Game, Score, Player, GamePlayer
from .forms import ScoreForm, PlayerSelectForm, PlayerForm

def live_game(request, game_id=None):
    if not game_id:
        game = Game.objects.create(
            date="2025-03-23 19:00",
            opponent="St. Mary’s",
            location="The Red Lion",
            game_type="regular",
            cycles_per_round=4
        )
        return redirect("live_game", game_id=game.id)

    game = Game.objects.get(id=game_id)
    scores = Score.objects.filter(game=game).order_by("round_number", "cycle_number")
    current_round = min(4, (scores.aggregate(Max("round_number"))["round_number__max"] or 0) + 1)
    current_cycle = min(game.cycles_per_round, (scores.filter(round_number=current_round).aggregate(Max("cycle_number"))["cycle_number__max"] or 0) + 1)

    round_players = GamePlayer.objects.filter(game=game, round_number=current_round)
    if not round_players and request.method != "POST":
        return render(request, "scores/select_players.html", {
            "game": game,
            "players": Player.objects.all(),
            "current_round": current_round,
            "form": PlayerSelectForm()
        })

    if request.method == "POST":
        if "select_players" in request.POST:
            form = PlayerSelectForm(request.POST)
            if form.is_valid():
                GamePlayer.objects.filter(game=game, round_number=current_round).delete()
                for player in form.cleaned_data["players"]:
                    GamePlayer.objects.create(game=game, player=player, round_number=current_round)
                return redirect("live_game", game_id=game.id)
        else:
            form = ScoreForm(request.POST)
            if form.is_valid():
                score = form.save(commit=False)
                if not score.player:
                    score.opponent_player_number = form.cleaned_data["opponent_player_number"]
                score.save()
                return redirect("live_game", game_id=game.id)
    else:
        form = ScoreForm(initial={"game": game, "round_number": current_round, "cycle_number": current_cycle})

    keiths_scores = scores.filter(player__isnull=False, round_number=current_round, cycle_number=current_cycle)
    opp_scores = scores.filter(player__isnull=True, round_number=current_round, cycle_number=current_cycle)
    keiths_cycle_total = keiths_scores.aggregate(Sum("total_score"))["total_score__sum"] or 0
    opp_cycle_total = opp_scores.aggregate(Sum("total_score"))["total_score__sum"] or 0
    keiths_round_total = scores.filter(player__isnull=False, round_number=current_round).aggregate(Sum("total_score"))["total_score__sum"] or 0
    opp_round_total = scores.filter(player__isnull=True, round_number=current_round).aggregate(Sum("total_score"))["total_score__sum"] or 0
    keiths_game_total = scores.filter(player__isnull=False).aggregate(Sum("total_score"))["total_score__sum"] or 0
    opp_game_total = scores.filter(player__isnull=True).aggregate(Sum("total_score"))["total_score__sum"] or 0

    score_differential = keiths_game_total - opp_game_total

    matchups = []
    keiths_players = list(keiths_scores.order_by("id"))
    opp_players = list(opp_scores.order_by("opponent_player_number"))
    for i in range(min(len(keiths_players), len(opp_players))):
        keith_player = keiths_players[i]
        opp_player = opp_players[i]
        matchups.append({
            "keith_name": keith_player.player.name,
            "keith_score": keith_player.total_score,
            "opp_name": f"{game.opponent} P{opp_player.opponent_player_number}",
            "opp_score": opp_player.total_score
        })

    return render(request, "scores/live_game.html", {
        "game": game,
        "keiths_scores": keiths_scores,
        "opp_scores": opp_scores,
        "current_round": current_round,
        "current_cycle": current_cycle,
        "round_players": round_players,
        "form": form,
        "keiths_cycle_total": keiths_cycle_total,
        "opp_cycle_total": opp_cycle_total,
        "keiths_round_total": keiths_round_total,
        "opp_round_total": opp_round_total,
        "keiths_game_total": keiths_game_total,
        "opp_game_total": opp_game_total,
        "score_differential": score_differential,
        "matchups": matchups
    })

def add_player(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("start_live_game")
    else:
        form = PlayerForm()
    return render(request, "scores/add_player.html", {"form": form})