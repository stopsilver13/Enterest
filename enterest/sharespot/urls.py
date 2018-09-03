from sharespot import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^register/review/$', views.register_review, name='register_review'),
    url(r'^register/review/date/$', views.get_date_list, name='get_date_list'),
    url(r'^register/review/time/$', views.get_time_list, name='get_time_list'),
    url(r'^register/review/seat/$', views.get_seat_list, name='get_seat_list'),
    url(r'^review/thanks/$', views.review_thanks, name='review_thanks'),

    url(r'^place/(?P<space>[\da-zA-Z-]+)/$', views.place_space, name='place_space'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/block/$', views.place_space_block, name='place_space_block'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/seat/$', views.place_space_seat, name='place_space_seat'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/like/$', views.space_like, name='space_like'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/basic/$', views.place_basic, name='place_basic'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/$', views.place_share, name='place_share'),

    # 장소 주변정보 ajax
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/edit/$', views.place_share_edit, name='place_share_edit'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/delete/$', views.place_share_delete, name='place_share_delete'),

    # 장소 주변정보 댓글 ajax
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/comment/create/$', views.place_share_comment_create, name='place_share_comment_create'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/comment/edit/$', views.place_share_comment_edit, name='place_share_comment_edit'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/comment/delete/$', views.place_share_comment_delete, name='place_share_comment_delete'),

    # 장소 주변정보 검색 ajax
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/search/$', views.place_share_search, name='place_share_search'),

    url(r'^series/list/$', views.series_list, name='series_list'),

    url(r'^series/(?P<series>[\da-zA-Z-]+)/like/$', views.series_like, name='series_like'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/basic/$', views.series_basic, name='series_basic'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/review/$', views.series_review, name='series_review'),

    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/$', views.series_talk_list, name='series_talk_list'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/(?P<topic>[\d]+)/$', views.series_talk, name='series_talk'),

    # 시리즈 와글 ajax
    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/(?P<topic>[\d]+)/create/$', views.series_talk_create, name='series_talk_create'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/(?P<topic>[\d]+)/edit/$', views.series_talk_edit, name='series_talk_edit'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/(?P<topic>[\d]+)/delete/$', views.series_talk_delete, name='series_talk_delete'),
]
