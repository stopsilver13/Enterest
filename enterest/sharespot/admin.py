from django.contrib import admin

from sharespot.models import (
    Category,
    Division,

    Place,
    Space,
    Section,
    Block,
    SeatLevel,
    Seat,
    SeatImg,
    SeatImgBadge,
    Structure,

    Series,
    SeriesImg,
    Event,
    Appear,

    Ticket,
    TicketImg,
    TicketDetail,
    Emotion,
    EventReview,
    EventReviewBadge,
    SeatReview,
    SeatReviewBadge,

    ShareInfoCategory,
    ShareInfo,
    ShareInfoImg,
    ShareInfoComment,
    TalkTopic,
    Talk,
)


admin.site.register(Category)
admin.site.register(Division)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'en_name', 'lat_lon']
    list_display_link = ['name']
    list_editable = ['lat_lon']
    list_filter = ['region']


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ['place', 'name', 'en_name']
    list_display_link = ['name']
    list_filter = ['place']


admin.site.register(Section)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'coordinate']
    list_display_link = ['name']
    list_editable = ['coordinate']
    list_filter = ['section__space']


@admin.register(SeatLevel)
class SeatLevelAdmin(admin.ModelAdmin):
    list_display = ['space', 'name', 'price', 'note']
    list_display_link = ['name']
    list_editable = ['note']
    list_filter = ['space']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['block', 'level', 'name']
    list_display_link = ['name']
    list_filter = ['block__section__space']


@admin.register(SeatImg)
class SeatImgAdmin(admin.ModelAdmin):
    list_display = ['seat', 'user', 'status', 'is_confirmed']
    list_display_link = ['seat', 'user']
    list_editable = ['is_confirmed']
    list_filter = ['seat__block__section__space', 'is_confirmed']


admin.site.register(SeatImgBadge)


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ['block', 'name']
    list_display_link = ['name']
    list_filter = ['block__section__space']


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ['division', 'name', 'space', 'start', 'end']
    list_display_link = ['name']
    list_filter = ['division', 'space']


admin.site.register(SeriesImg)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['series', 'name', 'start', 'end']
    list_display_link = ['series', 'name']
    list_filter = ['series']


@admin.register(Appear)
class AppearAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_team']
    list_display_link = ['name']
    list_filter = ['is_team']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']


admin.site.register(TicketImg)
admin.site.register(TicketDetail)
admin.site.register(Emotion)


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'total_star', 'anony_name', 'is_write_content', 'is_confirmed', 'created_at']
    list_editable = ['is_confirmed']
    list_filter = ['total_star', 'is_confirmed']

    def is_write_content(self, content):
        if content:
            return '리뷰작성'
        else:
            return '리뷰미작성'


admin.site.register(EventReviewBadge)


@admin.register(SeatReview)
class SeatReviewAdmin(admin.ModelAdmin):
    list_display = ['seat', 'view_star', 'real_star', 'anony_name', 'is_write_content', 'is_confirmed', 'created_at']
    list_editable = ['is_confirmed']
    list_filter = ['view_star', 'real_star', 'is_confirmed']

    def is_write_content(self, content):
        if content:
            return '리뷰작성'
        else:
            return '리뷰미작성'


admin.site.register(SeatReviewBadge)

admin.site.register(ShareInfoCategory)


@admin.register(ShareInfo)
class ShareInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'category', 'name', 'created_at']
    list_display_link = ['name']
    list_filter = ['place', 'category']


admin.site.register(ShareInfoImg)


@admin.register(ShareInfoComment)
class ShareInfoCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'share_info', 'content', 'created_at']


@admin.register(TalkTopic)
class TalkTopicAdmin(admin.ModelAdmin):
    list_display = ['user', 'series', 'content', 'created_at']
    list_display_link = ['content']
    list_filter = ['series']


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ['user', 'anony_name', 'topic', 'content', 'created_at']
    list_display_link = ['content']
    list_filter = ['topic']
