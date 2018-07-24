# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-07-24 04:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sharespot.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('is_team', models.BooleanField(default=False)),
                ('role', models.CharField(blank=True, max_length=20, null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='Appear/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('coordinate', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('en_name', models.CharField(max_length=30)),
                ('main_color', models.CharField(blank=True, max_length=10, null=True)),
                ('color', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('en_name', models.CharField(max_length=30)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Emotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20, null=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('appear_set', models.ManyToManyField(to='sharespot.Appear')),
            ],
        ),
        migrations.CreateModel(
            name='EventReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_star', models.PositiveSmallIntegerField(default=0)),
                ('content', models.TextField(blank=True, null=True)),
                ('anony_name', models.CharField(blank=True, max_length=10, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventReviewBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('en_name', models.CharField(max_length=30)),
                ('bg', models.ImageField(upload_to='Place/')),
                ('region', models.CharField(choices=[('Seoul', '서울'), ('Incheon', '인천'), ('Gyeonggi', '경기'), ('Busan', '부산'), ('Daejeon', '대전'), ('Daegu', '대구'), ('Gwangju', '광주'), ('Ulsan', '울산'), ('Gangwon', '강원'), ('ChungchungN', '충북'), ('ChungchungS', '충남'), ('GyeongsangN', '경북'), ('GyeongsangS', '경남'), ('JeonlaN', '전북'), ('JeonlaS', '전남'), ('Jeju', '제주')], max_length=10)),
                ('address', models.CharField(max_length=100)),
                ('lat_lon', models.CharField(max_length=20)),
                ('contact', models.CharField(blank=True, max_length=20, null=True)),
                ('website', models.CharField(blank=True, max_length=50, null=True)),
                ('explain', models.TextField(blank=True, null=True)),
                ('division_set', models.ManyToManyField(to='sharespot.Division')),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('row_real', models.CharField(max_length=20)),
                ('row', models.PositiveSmallIntegerField(default=0)),
                ('col', models.PositiveSmallIntegerField(default=0)),
                ('width', models.PositiveSmallIntegerField(default=1)),
                ('height', models.PositiveSmallIntegerField(default=1)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Block')),
            ],
        ),
        migrations.CreateModel(
            name='SeatImg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to=sharespot.models.seat_img_name)),
                ('status', models.CharField(choices=[('normalize', '가이드준수'), ('nozoom', 'zoom안함'), ('none', '해당사항없음')], default='none', max_length=10)),
                ('is_confirmed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SeatImgBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SeatLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('explain', models.CharField(blank=True, max_length=200, null=True)),
                ('note', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.PositiveIntegerField(default=0)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SeatReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_seat_name', models.CharField(max_length=100)),
                ('view_star', models.PositiveSmallIntegerField(default=0)),
                ('real_star', models.PositiveSmallIntegerField(default=0)),
                ('content', models.TextField(blank=True, null=True)),
                ('anony_name', models.CharField(blank=True, max_length=10, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SeatReviewBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('en_name', models.CharField(max_length=100)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('intro_title', models.CharField(max_length=100)),
                ('intro_content', models.TextField(blank=True, null=True)),
                ('announce', models.TextField(blank=True, null=True)),
                ('appear_link', models.URLField(blank=True, null=True)),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Division')),
                ('liker_set', models.ManyToManyField(related_name='liked_series_set', to=settings.AUTH_USER_MODEL)),
                ('seatlevel_set', models.ManyToManyField(to='sharespot.SeatLevel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SeriesImg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, null=True, upload_to='Series/')),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_set', to='sharespot.Series')),
            ],
        ),
        migrations.CreateModel(
            name='ShareInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('lat_lon', models.CharField(blank=True, max_length=20, null=True)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShareInfoCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('en_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ShareInfoComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('share_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.ShareInfo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShareInfoImg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, null=True, upload_to='ShareInfo/%Y/%m/%d')),
                ('info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_set', to='sharespot.ShareInfo')),
            ],
        ),
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('en_name', models.CharField(max_length=30)),
                ('division_set', models.ManyToManyField(to='sharespot.Division')),
                ('liker_set', models.ManyToManyField(related_name='liked_space_set', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Place')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('row', models.PositiveSmallIntegerField(default=0)),
                ('col', models.PositiveSmallIntegerField(default=0)),
                ('width', models.PositiveSmallIntegerField(default=1)),
                ('height', models.PositiveSmallIntegerField(default=1)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Block')),
            ],
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anony_name', models.CharField(blank=True, max_length=10, null=True)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TalkTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=100)),
                ('explain', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Series')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TicketDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=20)),
                ('content', models.TextField()),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Ticket')),
            ],
        ),
        migrations.CreateModel(
            name='TicketImg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, null=True, upload_to='ticket/%Y/%m/%d')),
                ('ticket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_set', to='sharespot.Ticket')),
            ],
        ),
        migrations.AddField(
            model_name='talk',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.TalkTopic'),
        ),
        migrations.AddField(
            model_name='talk',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shareinfo',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.ShareInfoCategory'),
        ),
        migrations.AddField(
            model_name='shareinfo',
            name='liker_set',
            field=models.ManyToManyField(related_name='liked_shareinfo_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shareinfo',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Place'),
        ),
        migrations.AddField(
            model_name='shareinfo',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='series',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Space'),
        ),
        migrations.AddField(
            model_name='section',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Space'),
        ),
        migrations.AddField(
            model_name='seatreview',
            name='badge_set',
            field=models.ManyToManyField(to='sharespot.SeatReviewBadge'),
        ),
        migrations.AddField(
            model_name='seatreview',
            name='history',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.RewardHistory'),
        ),
        migrations.AddField(
            model_name='seatreview',
            name='liker_set',
            field=models.ManyToManyField(related_name='liked_seatreview_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='seatreview',
            name='seat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Seat'),
        ),
        migrations.AddField(
            model_name='seatreview',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seat_review', to='sharespot.Ticket'),
        ),
        migrations.AddField(
            model_name='seatlevel',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Space'),
        ),
        migrations.AddField(
            model_name='seatimg',
            name='badge_set',
            field=models.ManyToManyField(to='sharespot.SeatImgBadge'),
        ),
        migrations.AddField(
            model_name='seatimg',
            name='history',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.RewardHistory'),
        ),
        migrations.AddField(
            model_name='seatimg',
            name='review',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sharespot.SeatReview'),
        ),
        migrations.AddField(
            model_name='seatimg',
            name='seat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_set', to='sharespot.Seat'),
        ),
        migrations.AddField(
            model_name='seatimg',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='seat',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.SeatLevel'),
        ),
        migrations.AddField(
            model_name='eventreview',
            name='badge_set',
            field=models.ManyToManyField(to='sharespot.EventReviewBadge'),
        ),
        migrations.AddField(
            model_name='eventreview',
            name='emotion_set',
            field=models.ManyToManyField(to='sharespot.Emotion'),
        ),
        migrations.AddField(
            model_name='eventreview',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Event'),
        ),
        migrations.AddField(
            model_name='eventreview',
            name='history',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.RewardHistory'),
        ),
        migrations.AddField(
            model_name='eventreview',
            name='liker_set',
            field=models.ManyToManyField(related_name='liked_eventreview_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventreview',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event_review', to='sharespot.Ticket'),
        ),
        migrations.AddField(
            model_name='event',
            name='series',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Series'),
        ),
        migrations.AddField(
            model_name='block',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharespot.Section'),
        ),
        migrations.AddField(
            model_name='appear',
            name='division_set',
            field=models.ManyToManyField(to='sharespot.Division'),
        ),
        migrations.AddField(
            model_name='appear',
            name='liker_set',
            field=models.ManyToManyField(related_name='liked_appear_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
