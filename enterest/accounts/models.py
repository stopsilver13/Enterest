from django.conf import settings
from django.db import models


class Profile(models.Model):

    SEX_CHOICES = (
        ('male', '남'),
        ('female', '여'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    img = models.ImageField(upload_to='profile/')  # 추후 업로드 경로 수정 & default 지정
    nick_name = models.CharField(max_length=8, blank=True, null=True)
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES,
        blank=True,
        null=True,
    )
    birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserReward(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward',
    )

    reward = models.IntegerField(default=0, editable=False)

    def __str__(self, **kwargs):
        return self.user.username + '의 리워드'

    def can_use_reward(self, amount):
        return self.reward >= amount
    # 보유 포인트보다 많은 포인트 사용 시도시 DataError

    def use_point(self, amount):
        self.reward -= amount
        self.save()

    def receive_point(self, amount):
        self.reward += amount
        self.save()


class RewardHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_history_set',
    )
    reason = models.CharField(max_length=30)
    amout = models.SmallIntegerField()
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# on_delete 이용해서 리뷰 삭제되면 히스토리도 삭제되고, 삭제시 해당 과정을 거꾸로 (적립이면 사용, 사용이면 적립) 하도록?


class GiftCategory(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Gift(models.Model):
    category = models.ForeignKey(GiftCategory, blank=True, null=True)
    name = models.CharField(max_length=20)
    price = models.PositiveIntegerField(default=0)
    img = models.ImageField(upload_to='gift/')  # 추후 업로드 경로 수정

    def __str__(self):
        return self.name


class GiftRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    gift = models.ForeignKey(Gift)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FAQCategory(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class FAQuestion(models.Model):
    category = models.ForeignKey(FAQCategory)
    title = models.CharField(max_length=100)
    answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
