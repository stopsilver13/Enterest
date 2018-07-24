from django.conf import settings
from django.db import models


def profile_img_name(instance, filename):
    return '/'.join(['Profile', instance.user.username, filename])


class Profile(models.Model):

    SEX_CHOICES = (
        ('male', '남'),
        ('female', '여'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    img = models.ImageField(upload_to=profile_img_name)  # default 지정
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
    STATUS_CHOICES = (
        ('ready', '지급대기'),
        ('complete', '지급완료'),
        ('reject', '취소/거절')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_history_set',
    )
    reason = models.CharField(max_length=30)
    amount = models.SmallIntegerField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ready',
    )
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 저장을 여기서 한번 해줘야 되나...
        if not self.is_complete:
            if self.status == 'complete':
                self.user.reward += self.amount
                self.user.reward.save()

                self.is_complete = True
                super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.is_complete:
            self.user.reward += (self.amount)*(-1)
            self.user.reward.save()

# on_delete 이용해서 리뷰 삭제되면 히스토리도 삭제되고, 삭제시 해당 과정을 거꾸로 (적립이면 사용, 사용이면 적립) 하도록?


class GiftCategory(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Gift(models.Model):
    category = models.ForeignKey(GiftCategory, blank=True, null=True)
    name = models.CharField(max_length=20)
    price = models.PositiveIntegerField(default=0)
    img = models.ImageField(upload_to='Gift/')

    def __str__(self):
        return self.name


class GiftRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    history = models.OneToOneField(RewardHistory)
    gift = models.ForeignKey(Gift)
    is_complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_complete:
            self.history.status = 'complete'
            self.history.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.history:
            self.history.delete()


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
