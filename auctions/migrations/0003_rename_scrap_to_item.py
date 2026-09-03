from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Renames Scrap -> Item and Auction.scrap -> Auction.item.

    RenameModel/RenameField preserve all existing rows and their data -
    nothing is deleted or recreated, only the model/table and field/column
    names change. Safe to run on a database that already has real auctions
    and bids in it (e.g. your live site).
    """
    dependencies = [
        ('auctions', '0002_scrap_created_at'),
    ]

    operations = [
        migrations.RenameModel(old_name='Scrap', new_name='Item'),
        migrations.RenameField(model_name='auction', old_name='scrap', new_name='item'),
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.CharField(
                blank=True, max_length=20,
                help_text='e.g. units, kg, Tons, Liters, pieces - leave blank if not applicable',
            ),
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['-created_at']},
        ),
    ]
