from sharespot import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^register/review/$', views.register_review, name='register_review'),

    url(r'^place/(?P<space>[\da-zA-Z-]+)/$', views.place_space, name='place_space'),
    # 장소/좌석뷰 - 블럭
    url(r'^place/(?P<space>[\da-zA-Z-]+)/basic/$', views.place_basic, name='place_basic'),
    url(r'^place/(?P<space>[\da-zA-Z-]+)/share/$', views.place_share, name='place_share'),

    url(r'^series/list/$', views.series_list, name='series_list'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/basic/$', views.series_basic, name='series_basic'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/review/$', views.series_review, name='series_review'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/$', views.series_talk_list, name='series_talk_list'),
    url(r'^series/(?P<series>[\da-zA-Z-]+)/talk/(?P<topic>[\d]+)/$', views.series_talk, name='series_talk'),
]
