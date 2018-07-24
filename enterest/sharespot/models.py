from collections import Counter

from django.conf import settings
from django.db import models

from accounts.models import RewardHistory


# TODO(완) : 좋아요/관심 공용 모델 > 좋아요와 관심등록은 같은 기능?!

class LikeMixinModel(models.Model):
    liker_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_%(class)s_set',
    )

    class Meta:
        abstract = True

    def count_liked(self):
        return self.liker_set.count()

    def is_liked_by(self, user):
        return self.liker_set.filter(pk=user.pk).exists()

    def toggle_like(self, user):
        liked_before = self.is_liked_by(user)
        if liked_before:
            self.liker_set.remove(user)
        else:
            self.liker_set.add(user)
        return not liked_before


class Category(models.Model):
    name = models.CharField(max_length=20)
    en_name = models.CharField(max_length=30)
    main_color = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Division(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=20)
    en_name = models.CharField(max_length=30)

    def __str__(self):
        division_name = self.category.name + '-' + self.name
        return division_name


# ### 장소/좌석 관련 모델 ### #

class Place(models.Model):

    REGION_CHOICES = (
        ('Seoul', '서울'),
        ('Incheon', '인천'),
        ('Gyeonggi', '경기'),
        ('Busan', '부산'),
        ('Daejeon', '대전'),
        ('Daegu', '대구'),
        ('Gwangju', '광주'),
        ('Ulsan', '울산'),
        ('Gangwon', '강원'),
        ('ChungchungN', '충북'),
        ('ChungchungS', '충남'),
        ('GyeongsangN', '경북'),
        ('GyeongsangS', '경남'),
        ('JeonlaN', '전북'),
        ('JeonlaS', '전남'),
        ('Jeju', '제주'),
    )

    name = models.CharField(max_length=20)
    en_name = models.CharField(max_length=30)
    bg = models.ImageField(upload_to='Place/')
    division_set = models.ManyToManyField(Division)
    region = models.CharField(
        max_length=10,
        choices=REGION_CHOICES,
    )
    address = models.CharField(max_length=100)
    lat_lon = models.CharField(max_length=20)  # float로 할까 고민되지만 일단 위도경도 묶어서 캐릭터로
    contact = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=50, blank=True, null=True)
    explain = models.TextField(blank=True, null=True)

    # 날씨 관련 속성 --> 일단은 보류

    def __str__(self):
        return self.name


class Space(LikeMixinModel):
    place = models.ForeignKey(Place)
    name = models.CharField(max_length=20)
    en_name = models.CharField(max_length=30)
    division_set = models.ManyToManyField(Division)

    def __str__(self):
        space_name = self.place.name + '-' + self.name
        return space_name

    def get_space_view_count(self):
        return SeatImg.objects.filter(seat__block__section__space=self).count()

    def get_space_review_count(self):
        return SeatReview.objects.filter(seat__block__section__space=self).count()

    def get_space_view_star(self):
        avg_dict = SeatReview.objects.filter(seat__block__section__space=self).aggregate(models.Avg('view_star'))  # 성능 의심되긴 함
        return avg_dict['view_star__avg']

    def get_space_real_star(self):
        avg_dict = SeatReview.objects.filter(seat__block__section__space=self).aggregate(models.Avg('real_star'))  # 성능 의심되긴 함
        return avg_dict['real_star__avg']


class Section(models.Model):
    space = models.ForeignKey(Space)
    name = models.CharField(max_length=20)

    def __str__(self):
        section_name = self.space.name + '-' + self.name
        return section_name


class Block(models.Model):
    section = models.ForeignKey(Section)
    name = models.CharField(max_length=20)
    coordinate = models.CharField(max_length=60)

    def __str__(self):
        block_name = self.section.space.name + '-' + self.name
        return block_name

    def get_block_color(self, series):
        # series = Series.objcets.get(en_name=series)
        level_list = Seat.objects.filter(block=self, level__series_set__in=series).values_list('level__pk')
        if len(level_list) == 0:
            main_color = '#fff'  # 좌석이 없는 블럭 색: 일단 흰색으로

        else:
            main_level_pk = Counter(level_list).most_common(1)[0][0]
            main_color = SeatLevel.objects.get(pk=main_level_pk).color
        return main_color


class SeatLevel(models.Model):
    space = models.ForeignKey(Space)
    name = models.CharField(max_length=20)
    explain = models.CharField(max_length=200, blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)  # 어드민용
    price = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=10)

    def __str__(self):
        level_name = self.space.name + '-' + self.name
        return level_name


class Seat(models.Model):
    # space = models.ForeignKey(Space)
    block = models.ForeignKey(Block)
    level = models.ForeignKey(SeatLevel)
    name = models.CharField(max_length=20)
    row_real = models.CharField(max_length=20)

    # 왼쪽/위 모서리 기준
    row = models.PositiveSmallIntegerField(default=0)
    col = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=1)
    height = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        seat_name = self.block.name + '-' + self.name
        return seat_name


def seat_img_name(instance, filename):
    return '/'.join(['seat/img', instance.seat.block.section.space.place, instance.seat.block.section.space, instance.seat.block.section, instance.seat.block, filename])


class SeatImg(models.Model):

    ZOOM_CHOICES = (
        ('normalize', '가이드준수'),
        ('nozoom', 'zoom안함'),
        ('none', '해당사항없음'),
    )

    seat = models.ForeignKey(
        Seat,
        related_name='image_set',
        blank=True,
        null=True,
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    history = models.OneToOneField(RewardHistory, blank=True, null=True)
    review = models.ForeignKey('SeatReview', blank=True, null=True)  # 좀 고민됨
    img = models.ImageField(upload_to=seat_img_name)

    status = models.CharField(
        max_length=10,
        choices=ZOOM_CHOICES,
        default='none',
    )  # no zoom이면 노줌 뱃지 / # normalize이면 가이드준수 뱃지

    badge_set = models.ManyToManyField('SeatImgBadge')  # 등록시 자동지급

    is_confirmed = models.BooleanField(default=False)  # True이면 공개

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_confirmed:
            self.history.status = 'complete'
            self.history.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.history:
            self.history.delete()


class SeatImgBadge(models.Model):
    name = models.CharField(max_length=10)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Structure(models.Model):
    # space = models.ForeignKey(Space)
    block = models.ForeignKey(Block)
    name = models.CharField(max_length=20)

    # 왼쪽/위 모서리 기준
    row = models.PositiveSmallIntegerField(default=0)
    col = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=1)
    height = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        structure_name = self.block.name + '-' + self.name
        return structure_name


# ### 이벤트/공연/경기 관련 모델 ### #

class Series(LikeMixinModel):
    division = models.ForeignKey(Division)
    name = models.CharField(max_length=20)
    en_name = models.CharField(max_length=100)
    start = models.DateField()
    end = models.DateField()
    space = models.ForeignKey(Space)
    seatlevel_set = models.ManyToManyField(SeatLevel)

    intro_title = models.CharField(max_length=100)
    intro_content = models.TextField(blank=True, null=True)
    announce = models.TextField(blank=True, null=True)
    appear_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_series_review_count(self):
        return EventReview.objects.filter(event__series=self).count()

    def get_series_star(self):
        avg_dict = EventReview.objects.filter(event__series=self).aggregate(models.Avg('total_star'))  # 성능 의심되긴 함
        return avg_dict['total_star__avg']

    def get_star_num(self):
        star_num_list = []
        for i in range(1, 6):
            star_num_list.append(EventReview.objects.filter(event__series=self, total_star=i).count())
        return star_num_list


class SeriesImg(models.Model):
    series = models.ForeignKey(
        Series,
        related_name='image_set',
        blank=True,
        null=True,
    )
    img = models.ImageField(upload_to='Series/', blank=True, null=True)


class Event(models.Model):
    series = models.ForeignKey(Series)
    name = models.CharField(max_length=20, blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    appear_set = models.ManyToManyField('Appear')

    def __str__(self):
        event_name = self.series.name + '-' + str(self.start.strftime("%Y. %m. %d."))
        return event_name

    def get_event_star(self):
        avg_dict = self.eventreview_set.all().aggregate(models.Avg('total_star'))
        return avg_dict['total_star__avg']


class Appear(LikeMixinModel):
    name = models.CharField(max_length=20)
    division_set = models.ManyToManyField(Division)
    is_team = models.BooleanField(default=False)
    role = models.CharField(max_length=20, blank=True, null=True)
    img = models.ImageField(upload_to='Appear/', blank=True, null=True)  # default 지정

    def __str__(self):
        return self.name


# ### 티켓/리뷰 관련 모델 ### #
# TODO : 블럭/좌석/이벤트별 뷰/리뷰 갯수 뽑아올 수 있는 함수

class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        ticket_name = self.user.username + ' -' + str(self.pk)
        return ticket_name

    def is_complete(self):
        if self.event_review.content and self.seat_review.content:
            return True
        else:
            return False


class TicketImg(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        related_name='image_set',
        blank=True,
        null=True,
    )
    img = models.ImageField(upload_to='ticket/%Y/%m/%d', blank=True, null=True)  # default는 기본 이미지

    def __str__(self):
        img_name = self.ticket.user.username + ' -' + str(self.ticket.pk)
        return img_name


class TicketDetail(models.Model):
    ticket = models.ForeignKey(Ticket)
    index = models.CharField(max_length=20)
    content = models.TextField()

    def __str__(self):
        detail_name = self.ticket.user.username + ' -' + str(self.ticket.pk) + ' : ' + self.index
        return detail_name


class Emotion(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def get_quote_count(self):
        return self.eventreview_set.count()  # 작동 여부 점검 필요


class EventReview(LikeMixinModel):
    ticket = models.OneToOneField(Ticket, related_name='event_review')
    history = models.OneToOneField(RewardHistory, blank=True, null=True)
    event = models.ForeignKey(Event)
    total_star = models.PositiveSmallIntegerField(default=0)
    content = models.TextField(blank=True, null=True)
    emotion_set = models.ManyToManyField(Emotion)
    badge_set = models.ManyToManyField('EventReviewBadge')
    anony_name = models.CharField(max_length=10, blank=True, null=True)

    is_confirmed = models.BooleanField(default=False)  # True이면 공개

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        review_name = self.event.series.name
        return review_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_confirmed:
            self.history.status = 'complete'
            self.history.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.history:
            self.history.delete()


class EventReviewBadge(models.Model):
    name = models.CharField(max_length=10)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class SeatReview(LikeMixinModel):
    ticket = models.OneToOneField(Ticket, related_name='seat_review')
    history = models.OneToOneField(RewardHistory, blank=True, null=True)
    seat = models.ForeignKey(Seat)
    real_seat_name = models.CharField(max_length=100)
    view_star = models.PositiveSmallIntegerField(default=0)
    real_star = models.PositiveSmallIntegerField(default=0)
    content = models.TextField(blank=True, null=True)
    badge_set = models.ManyToManyField('SeatReviewBadge')
    anony_name = models.CharField(max_length=10, blank=True, null=True)

    is_confirmed = models.BooleanField(default=False)  # True이면 공개

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        review_name = self.seat.block.section.space.name + ' ' + self.seat.block.name + '블럭 ' + self.seat.name
        return review_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_confirmed:
            self.history.status = 'complete'
            self.history.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.history:
            self.history.delete()


class SeatReviewBadge(models.Model):
    name = models.CharField(max_length=10)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


# ### 장소 > 정보공유 관련 모델 ### #

class ShareInfoCategory(models.Model):
    name = models.CharField(max_length=10)
    en_name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ShareInfo(LikeMixinModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
    )
    place = models.ForeignKey(Place)
    category = models.ForeignKey(ShareInfoCategory)  # ManyToMany랑 고민됨

    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100, blank=True, null=True)
    lat_lon = models.CharField(max_length=20, blank=True, null=True)  # float로 할까 고민되지만 일단 위도경도 묶어서 캐릭터로
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        info_name = self.place.name + ' - ' + self.name
        return info_name


class ShareInfoImg(models.Model):
    info = models.ForeignKey(
        ShareInfo,
        related_name='image_set',
    )
    img = models.ImageField(upload_to='ShareInfo/%Y/%m/%d', blank=True, null=True)


class ShareInfoComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    share_info = models.ForeignKey(ShareInfo)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


# ### 이벤트 > 딥톡 관련 모델 ### #

class TalkTopic(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    series = models.ForeignKey(Series)
    content = models.CharField(max_length=100)
    explain = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        topic_name = self.series.name + ' - ' + self.content
        return topic_name

    @property  # 이렇게 해도 되나 모름...
    def is_joined(self, user):
        result = Talk.objects.filter(user=user, topic=self).exists()
        return result


class Talk(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    anony_name = models.CharField(max_length=10, blank=True, null=True)
    topic = models.ForeignKey(TalkTopic)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
