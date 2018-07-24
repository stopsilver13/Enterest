from django.contrib import admin

from accounts.models import (
    Profile,
    UserReward,
    RewardHistory,

    GiftCategory,
    Gift,
    GiftRequest,

    FAQCategory,
    FAQuestion,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nick_name', 'sex', 'birth', 'created_at']
    list_display_link = ['user', 'nick_name']


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward']
    list_display_link = ['user']


@admin.register(RewardHistory)
class RewardHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'reason', 'amount', 'status', 'is_complete', 'created_at']
    list_display_link = ['user', 'reason']
    list_editable = ['is_complete']
    list_filter = ['reason', 'status', 'is_complete']


admin.site.register(GiftCategory)


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_filter = ['category']


@admin.register(GiftRequest)
class GiftRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'gift', 'is_complete', 'created_at']
    list_display_link = ['user', 'gift']
    list_editable = ['is_complete']
    list_filter = ['is_complete']


admin.site.register(FAQCategory)


@admin.register(FAQuestion)
class FAQuestionAdmin(admin.ModelAdmin):
    list_display = ['category', 'title']
    list_display_link = ['title']
    list_filter = ['category']
