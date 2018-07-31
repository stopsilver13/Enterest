from accounts import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url

urlpatterns = [

    url(r'^login/$', views.login_custom, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/info/$', views.signup_info, name='signup_info'),

    url(r'^myticket/$', views.myticket, name='myticket'),
    url(r'^mywriting/$', views.mywriting, name='mywriting'),
    url(r'^mylike/$', views.mylike, name='mylike'),
    url(r'^myreward/$', views.myreward, name='myreward'),
    url(r'^myinfo/$', views.myinfo, name='myinfo'),
    url(r'^myinfo/check/pw/$', views.checking_pw, name='checking_pw'),  # 비밀번호 확인 ajax
    url(r'^faq/$', views.faqlist, name='faqlist'),

    url(r'^user/delete/$', views.user_delete, name='user_delete'),
]
