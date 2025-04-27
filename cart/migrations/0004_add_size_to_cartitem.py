from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_alter_cartitem_unique_together_alter_cartitem_size_and_more"),
    ]

    operations = [
        # 1) Add the column, allow NULLs so existing rows don’t break
        migrations.AddField(
            model_name="cartitem",
            name="size",
            field=models.ForeignKey(
                to="shop.Size",
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
            ),
        ),
        # 2) (Optional) If you want to enforce NOT NULL going forward,
        #    you can then alter it—but you can also leave it nullable.
        migrations.AlterField(
            model_name="cartitem",
            name="size",
            field=models.ForeignKey(
                to="shop.Size",
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
    ]
