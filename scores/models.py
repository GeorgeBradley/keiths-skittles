from django.db import models

class Game(models.Model):
    date = models.DateTimeField()
    opponent = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    game_type = models.CharField(max_length=10, choices=[("regular", "Regular"), ("first_pin", "First Pin")], default="regular")
    cycles_per_round = models.IntegerField(default=4)

    def __str__(self):
        return f"{self.date} vs {self.opponent}"

class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round_number = models.IntegerField(choices=[(i, i) for i in range(1, 5)])

    class Meta:
        unique_together = ("game", "player", "round_number")

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    round_number = models.IntegerField(choices=[(i, i) for i in range(1, 5)])
    cycle_number = models.IntegerField()
    roll_1 = models.IntegerField(default=0)
    roll_2 = models.IntegerField(default=0)
    roll_3 = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    first_pin_success = models.IntegerField(null=True, blank=True)
    opponent_player_number = models.IntegerField(null=True, blank=True)
    is_strike = models.BooleanField(default=False)
    is_spare = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        total_pins = 9  # Assuming 9-pin skittles
        self.total_score = self.roll_1 + self.roll_2 + self.roll_3
        self.is_strike = (self.roll_1 == total_pins)
        self.is_spare = (not self.is_strike and (self.roll_1 + self.roll_2) == total_pins)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Round {self.round_number}, Cycle {self.cycle_number}: {self.total_score}"