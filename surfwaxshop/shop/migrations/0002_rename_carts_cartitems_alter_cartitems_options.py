# Generated by Django 5.0 on 2023-12-18 19:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Carts',
            new_name='CartItems',
        ),
        migrations.AlterModelOptions(
            name='cartitems',
            options={'verbose_name': 'Cart', 'verbose_name_plural': 'Carts'},
        ),
    ]
