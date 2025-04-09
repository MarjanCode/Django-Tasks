# Generated by Django 5.1.7 on 2025-04-09 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('Phones', 'phones'), ('Smart watches', 'smart watches'), ('Cameras', 'cameras'), ('Headphones', 'headphones'), ('Computers', 'computers'), ('Gaming', 'gaming')], max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('color', models.CharField(max_length=30)),
                ('brand', models.CharField(max_length=50)),
                ('builtin_memory', models.CharField(max_length=50)),
                ('protection_class', models.CharField(max_length=50)),
                ('screen_diagonal', models.FloatField()),
                ('screen_type', models.CharField(max_length=100)),
                ('battery_capacity', models.IntegerField()),
                ('main_camera', models.CharField(max_length=100)),
                ('front_camera', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'products',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(max_length=255)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
            options={
                'db_table': 'images',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product')),
            ],
            options={
                'db_table': 'reviews',
            },
        ),
    ]
