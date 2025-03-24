from django.shortcuts import render, redirect
from django.db.models import Sum, Max
from .models import Game, Score, Player, GamePlayer
from .forms import ScoreForm, PlayerSelectForm, PlayerForm, GameSetupForm

def start_game(request):
    if request.method == "POST":
        form = GameSetupForm(request.POST)
        if form.is_valid():
            game = form.save()
            request.session['game_id'] = game.id  # Store game_id in session
            return redirect("live_game", game_id=game.id)
    else:
        form = GameSetupForm(initial={
            'date': "2025-03-23T19:00",
            'opponent': "St. Mary’s",
            'location': "The Red Lion",
            'game_type': "regular",
            'cycles_per_round': 4,
            'first_team': 'keith'
        })
    return render(request, "scores/start_game.html", {"form": form})

def live_game(request, game_id=None):
    # Check if a game_id is stored in the session
    if not game_id and 'game_id' in request.session:
        game_id = request.session['game_id']

    if not game_id:
        return redirect("start_game")

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

    # Determine the next expected player in the sequence
    current_scores = scores.filter(round_number=current_round, cycle_number=current_cycle).order_by("id")
    round_player_ids = list(round_players.values_list("player_id", flat=True))
    expected_players = []
    for i in range(len(round_player_ids)):
        if game.first_team == 'keith':
            expected_players.append(("keith", i + 1))  # Keith's player
            expected_players.append(("opponent", i + 1))  # Opponent player
        else:
            expected_players.append(("opponent", i + 1))  # Opponent player
            expected_players.append(("keith", i + 1))  # Keith's player
    current_position = len(current_scores) % (len(round_player_ids) * 2)
    if current_position < len(expected_players):
        next_team, next_position = expected_players[current_position]
    else:
        # Move to the next cycle or round
        if current_cycle < game.cycles_per_round:
            current_cycle += 1
        elif current_round < 4:
            current_round += 1
            current_cycle = 1
            GamePlayer.objects.filter(game=game, round_number=current_round-1).delete()
            return redirect("live_game", game_id=game.id)
        else:
            # Game is over - redirect to a summary page (to be implemented)
            return redirect("live_game", game_id=game.id)
        next_team, next_position = expected_players[0]  # Reset to first player in sequence

    if request.method == "POST":
        if "select_players" in request.POST:
            form = PlayerSelectForm(request.POST)
            if form.is_valid():
                GamePlayer.objects.filter(game=game, round_number=current_round).delete()
                for player in form.cleaned_data["players"]:
                    GamePlayer.objects.create(game=game, player=player, round_number=current_round)
                return redirect("live_game", game_id=game.id)
            else:
                print("PlayerSelectForm errors:", form.errors)
        else:
            form = ScoreForm(request.POST)
            if form.is_valid():
                score = form.save(commit=False)
                score.game = game
                score.round_number = current_round
                score.cycle_number = current_cycle
                if not score.player:
                    score.opponent_player_number = form.cleaned_data["opponent_player_number"]
                score.save()
                print("Saved Score:", score.roll_1, score.roll_2, score.roll_3, score.total_score)
                return redirect("live_game", game_id=game.id)
            else:
                print("ScoreForm errors:", form.errors)
    else:
        form = ScoreForm(initial={"game": game, "round_number": current_round, "cycle_number": current_cycle})
        if next_team == "keith":
            form.fields['opponent_player_number'].widget = forms.HiddenInput()
        elif next_team == "opponent":
            form.fields['player'].widget = forms.HiddenInput()
            form.fields['opponent_player_number'].initial = next_position

    keiths_scores = scores.filter(player__isnull=False, round_number=current_round, cycle_number=current_cycle)
    opp_scores = scores.filter(player__isnull=True, round_number=current_round, cycle_number=current_cycle)
    print("Keith's Scores:", list(keiths_scores.values('roll_1', 'roll_2', 'roll_3', 'total_score')))
    print("Opponent Scores:", list(opp_scores.values('roll_1', 'roll_2', 'roll_3', 'total_score')))
    keiths_cycle_total = keiths_scores.aggregate(Sum("total_score"))["total_score__sum"] or 0
    opp_cycle_total = opp_scores.aggregate(Sum("total_score"))["total_score__sum"] or 0
    keiths_round_total = scores.filter(player__isnull=False, round_number=current_round).aggregate(Sum("total_score"))["total_score__sum"] or 0
    opp_round_total = scores.filter(player__isnull=True, round_number=current_round).aggregate(Sum("total_score"))["total_score__sum"] or 0
    keiths_game_total = scores.filter(player__isnull=False).aggregate(Sum("total_score"))["total_score__sum"] or 0
    opp_game_total = scores.filter(player__isnull=True).aggregate(Sum("total_score"))["total_score__sum"] or 0
    print("Cycle Totals - Keith:", keiths_cycle_total, "Opponent:", opp_cycle_total)
    print("Round Totals - Keith:", keiths_round_total, "Opponent:", opp_round_total)
    print("Game Totals - Keith:", keiths_game_total, "Opponent:", opp_game_total)

    score_differential = keiths_game_total - opp_game_total
    print("Score Differential:", score_differential)

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
        "matchups": matchups,
        "next_team": next_team,
        "next_position": next_position
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