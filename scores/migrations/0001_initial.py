# Generated by Django 5.1.7 on 2025-03-23 23:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('opponent', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('game_type', models.CharField(choices=[('regular', 'Regular'), ('first_pin', 'First Pin')], default='regular', max_length=10)),
                ('cycles_per_round', models.IntegerField(default=4)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('cycle_number', models.IntegerField()),
                ('roll_1', models.IntegerField(default=0)),
                ('roll_2', models.IntegerField(default=0)),
                ('roll_3', models.IntegerField(default=0)),
                ('total_score', models.IntegerField(default=0)),
                ('first_pin_success', models.IntegerField(blank=True, null=True)),
                ('opponent_player_number', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scores.game')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scores.player')),
            ],
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scores.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scores.player')),
            ],
            options={
                'unique_together': {('game', 'player', 'round_number')},
            },
        ),
    ]
