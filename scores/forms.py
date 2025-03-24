from django import forms
from .models import Score, Player, GamePlayer

class ScoreForm(forms.ModelForm):
    player = forms.ModelChoiceField(queryset=Player.objects.all(), empty_label="Select Keith’s Player", required=False)
    opponent_player_number = forms.ChoiceField(choices=[(i, f"P{i}") for i in range(1, 4)], label="Opponent Player", required=False)

    class Meta:
        model = Score
        fields = ["player", "game", "round_number", "cycle_number", "roll_1", "roll_2", "roll_3", "first_pin_success", "opponent_player_number"]

    def clean(self):
        cleaned_data = super().clean()
        player = cleaned_data.get("player")
        opp_num = cleaned_data.get("opponent_player_number")
        roll_1 = cleaned_data.get("roll_1", 0)
        roll_2 = cleaned_data.get("roll_2", 0)
        roll_3 = cleaned_data.get("roll_3", 0)

        if player and opp_num:
            raise forms.ValidationError("Choose either Keith’s player or an opponent player, not both.")
        if not player and not opp_num:
            raise forms.ValidationError("Select a player or opponent number.")

        max_pins = 9
        for roll, value in [("Roll 1", roll_1), ("Roll 2", roll_2), ("Roll 3", roll_3)]:
            if value < 0 or value > max_pins:
                raise forms.ValidationError(f"{roll} must be between 0 and {max_pins}.")

        return cleaned_data

class PlayerSelectForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = GamePlayer
        fields = []

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name']