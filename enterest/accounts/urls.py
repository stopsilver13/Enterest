from accounts import views
from django.conf.urls import url

urlpatterns = [
    # 로그인
    # 회원가입

    url(r'^myticket/$', views.myticket, name='myticket'),
    url(r'^mywriting/$', views.mywriting, name='mywriting'),
    url(r'^mylike/$', views.mylike, name='mylike'),
    url(r'^myreward/$', views.myreward, name='myreward'),
    url(r'^myinfo/$', views.myinfo, name='myinfo'),
    url(r'^faq/$', views.faqlist, name='faqlist'),
]
