# Generated by Django 5.1.2 on 2024-10-13 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='photos/')),
                ('predict', models.CharField(max_length=20)),
                ('x1', models.IntegerField()),
                ('y1', models.IntegerField()),
                ('x2', models.IntegerField()),
                ('y2', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=150)),
                ('count_defects', models.IntegerField()),
                ('count_photos', models.IntegerField()),
                ('resume', models.CharField(max_length=30)),
                ('dead_pixels', models.IntegerField()),
                ('scratches', models.IntegerField()),
                ('lock', models.IntegerField()),
                ('chip', models.IntegerField()),
                ('missing_screw', models.IntegerField()),
                ('keyboard_defect', models.IntegerField()),
            ],
        ),
    ]
