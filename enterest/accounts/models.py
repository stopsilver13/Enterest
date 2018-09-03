from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models


# TODO: 멤버십
class Membership(models.Model):
    level = models.CharField(max_length=20)

    def __str__(self):
        return self.level


class MembershipCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    membership = models.ForeignKey(Membership)
    expiration = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' - ' + self.membership.level


def profile_img_name(instance, filename):
    return '/'.join(['Profile', instance.user.username, filename])


class Profile(models.Model):

    SEX_CHOICES = (
        ('male', '남'),
        ('female', '여'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    code = models.CharField(max_length=10)
    img = models.ImageField(upload_to=profile_img_name, blank=True, null=True)  # 추후에 다시 디폴트 지정
    nick_name = models.CharField(max_length=8, blank=True, null=True)
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES,
        blank=True,
        null=True,
    )
    birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    is_blacklist = models.BooleanField(default=False)

    reported_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='reported_%(class)s_set',
        blank=True,
    )

    def count_reported(self):
        return self.reported_set.count()

    def is_reported_by(self, user):
        return self.reported_set.filter(pk=user.pk).exists()

    def toggle_report(self, user):
        reported_before = self.is_reported_by(user)
        if reported_before:
            self.reported_set.remove(user)
        else:
            self.reported_set.add(user)
        return not reported_before

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
    amount = models.FloatField()
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
        if not self.is_complete:
            if self.status == 'complete':
                self.user.reward.reward += self.amount
                self.user.reward.save()

                self.is_complete = True
                super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.is_complete:
            self.user.reward.reward += (self.amount)*(-1)
            self.user.reward.save()

    def __str__(self):
        return self.user.username + '-' + self.reason

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
            super().save(*args, **kwargs)

            self.history.status = 'complete'
            self.history.save()

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
