from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("league", "0002_sponsor"),
    ]

    operations = [
        migrations.AddField(
            model_name="matchday",
            name="score_multiplier",
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text="1 = puntuación normal, 2 = doble puntuación, etc.",
            ),
        ),
    ]