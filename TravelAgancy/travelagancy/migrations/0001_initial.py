# Generated by Django 3.2.13 on 2023-01-07 19:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('leave_city', models.CharField(max_length=100, null=True)),
                ('arrive_city', models.CharField(max_length=100, null=True)),
                ('leave_airport', models.CharField(max_length=100, null=True)),
                ('arrive_airport', models.CharField(max_length=100, null=True)),
                ('leave_time', models.DateTimeField(null=True)),
                ('arrive_time', models.DateTimeField(null=True)),
                ('capacity', models.IntegerField(default=0, null=True)),
                ('num_of_rows', models.IntegerField(default=0, null=True)),
                ('seats_in_row', models.IntegerField(default=0, null=True)),
                ('price', models.FloatField(default=0, null=True)),
                ('book_sum', models.IntegerField(default=0, null=True)),
                ('income', models.FloatField(default=0, null=True)),
                ('user', models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.IntegerField(default=1, null=True)),
                ('seat_letter', models.CharField(max_length=3, null=True)),
                ('busy', models.BooleanField(default=False, null=True)),
                ('flight', models.ManyToManyField(default=1, to='travelagancy.Flight')),
                ('user', models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('ps_id', models.IntegerField(default=1, null=True)),
                ('ps_number', models.IntegerField(default=1, null=True)),
                ('isPay', models.BooleanField(default=False, null=True)),
                ('flight', models.ManyToManyField(default=1, to='travelagancy.Flight')),
                ('seat', models.ManyToManyField(default=1, to='travelagancy.Seat')),
                ('user', models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=100, null=True)),
                ('cardnum', models.CharField(max_length=100, null=True)),
                ('userid', models.CharField(max_length=100, null=True)),
                ('user', models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
