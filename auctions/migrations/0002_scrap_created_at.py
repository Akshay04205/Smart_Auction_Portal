from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    """
    Adds Scrap.created_at as its own migration (rather than baking it into
    0001_initial) so this works correctly whether you're setting up the
    database for the first time OR you already ran `migrate` back in
    Phase 1 - either way, Django will apply this one and add the column.

    Existing Scrap rows get created_at set to "now" at migration time
    (there's no way to know their real creation time retroactively).
    """
    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrap',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='scrap',
            options={'ordering': ['-created_at']},
        ),
    ]
