from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import login as auth_login
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.shortcuts import render, redirect

from sharespot.models import Series, Ticket, TalkTopic
from accounts.models import Membership, MembershipCard, Profile, UserReward, RewardHistory, Gift, GiftRequest, FAQCategory

from accounts.forms import ImageUploadForm

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.templatetags.socialaccount import get_providers

from datetime import datetime, timedelta


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('/accounts/signup/info/?next='+request.GET.get('next', '/'))

    return render(request, 'accounts/signup.html')


def signup_info(request):
    user = request.user
    has_profile = Profile.objects.filter(user=user).exists()
    # if has_profile:
    #     return redirect(request.GET.get('next', '/'))

    year = [x for x in range(2017, 1950, -1)]
    month = [x for x in range(1, 13)]
    day = [x for x in range(1, 32)]

    if request.method == 'POST':
        code = get_random_string(length=5) + '-' + str(user.pk)
        email = request.POST.get('email')
        nick_name = request.POST.get('nick_name')
        sex = request.POST.get('sex')
        birth = request.POST.get('year') + '-' + request.POST.get('month') + '-' + request.POST.get('day')
        phone = request.POST.get('phone')

        user.email = email
        user.save()

        Profile.objects.create(user=user, code=code, nick_name=nick_name, sex=sex, birth=birth, phone=phone)

        friend_code = request.POST.get('friend_code')

        if Profile.objects.filter(code=friend_code).exists():
            friend = Profile.objects.get(code=friend_code).user
            RewardHistory.objects.create(
                user=friend,
                reason='{}님의 추천코드 입력'.format(user.username),
                amount=10,
                status='complete',
            )

        UserReward.objects.create(user=user)

        # basic 멤버십 60일 무료
        MembershipCard.objects.create(
            user=user,
            membership=Membership.objects.get(level='basic'),
            expiration=datetime.now() + timedelta(days=60),
        )

        return redirect(request.GET.get('next', '/'))

    return render(request, 'accounts/signup_info.html', {
        'year': year,
        'month': month,
        'day': day,
    })


def login_custom(request):
    providers = []

    for provider in get_providers():  # 활성화된 provider 목록을 가져옴.
        try:
            provider.social_app = SocialApp.objects.get(provider=provider.id, sites=settings.SITE_ID)
        except SocialApp.DoesNotExist:
            provider.social_app = None
        providers.append(provider)

    return auth_login(request,
                      template_name='accounts/login.html',
                      extra_context={'providers': providers})


@login_required
def myinfo(request):
    user = request.user

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user.profile.img = form.cleaned_data['image']

        new_pw1 = request.POST.get('new_password1')
        nick_name = request.POST.get('nick_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if new_pw1 != '':
            user.set_password(new_pw1)
        if nick_name != '':
            user.profile.nick_name = nick_name
        if email != '':
            user.email = email
        if phone != '':
            user.profile.phone = phone

        # 관심태그는 아에 따로 ajax 빼야할듯

        user.save()
        user.profile.save()

        return redirect('/accounts/myinfo/')

    return render(request, 'accounts/myinfo.html', {
        'user': user,
    })


def checking_pw(request):
    # 유저가 프로필 수정을 누르면 old_pw, new_pw1/2가 빈칸인지 아닌지를 판별 -> 모두 빈칸이 아니면 셋 다 채워져 있는지 판별 -> 셋다 채워져 있을 경우, new_pw1/2가 일치하는지 판별 -> 모두 빈칸이라면 바로 submit, 일부만 채워져 있으면 submit 막고 "비밀번호 변경을 원하시면 모두 채워주세요" 알림, 셋다 채워져 있고 new_pw1/2 일치하면 여기로 보내고 'match' 뜨면 submit, 일치하지 않으면 "변경하시고자 하는 비밀번호와 비밀번호 확인이 일치하지 않습니다" 알림

    if request.method == 'POST':
        user = request.user
        old_pw = request.POST.get('old_password')
        if user.check_password(old_pw):
            return HttpResponse('match')
        else:
            return HttpResponse('mis_match')


def user_delete(request):
    user = request.user
    user.delete()

    return redirect('/')


def report_user(request, writer):
    user = request.user
    writer = User.objects.get(pk=writer)

    if request.method == 'POST':
        writer.profile.toggle_report(user)
        if user in writer.profile.reported_set.all():
            return HttpResponse('complete')
        else:
            return HttpResponse('canceled')
    return render(request)


@login_required
def myticket(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user)

    return render(request, 'accounts/myticket.html', {
        'user': user,
        'tickets': tickets,
    })


@login_required
def mylike(request):
    user = request.user
    now = datetime.now()

    # 관심 appear들의 다가오는 이벤트를 한 쿼리셋으로 묶기; 방법이 구린거 같아서 추후 성능보고 좀더 고민 ㅠ.ㅠ
    appear_series = []
    for appear in user.liked_appear_set.all():
        appear_series += appear.event_set.filter(start__lte=now).values_list('series__pk', flat=True)
        print(appear_series)

    queryset = Series.objects.none()
    for series in list(set(appear_series))[:25]:
        queryset = queryset | Series.objects.filter(pk=series)

    queryset = queryset.order_by('start')

    return render(request, 'accounts/mylike.html', {
        'user': user,
        'queryset': queryset,
    })


@login_required
def mywriting(request):
    user = request.user
    topics = user.talk_set.values_list('topic__pk', flat=True)

    joined_topics = TalkTopic.objects.none()
    for topic in list(set(topics)):
        joined_topics = joined_topics | TalkTopic.objects.filter(pk=topic)

    return render(request, 'accounts/mywriting.html', {
        'user': user,
        'joined_topics': joined_topics,
    })


@login_required
def myreward(request):
    user = request.user
    gifts = Gift.objects.all()

    # 리워드 요청
    if request.method == 'POST':
        # 유저 휴대폰번호 입력값으로 업데이트
        user.profile.phone = request.POST.get('phone')
        user.save()

        gift = Gift.objects.get(pk=request.POST.get('gift'))

        # 교환권 요청 및 리워드 사용 히스토리 생성
        history = RewardHistory.objects.create(
            user=user,
            reason=gift.name + ' 교환',
            amount=gift.price*(-1),
        )
        GiftRequest.objects.create(user=user, gift=gift, history=history)

        return redirect(request.path)

    return render(request, 'accounts/myreward.html', {
        'user': user,
        'gifts': gifts,
    })


def faqlist(request):
    faq_category = FAQCategory.objects.all()

    return render(request, 'accounts/faqlist.html', {
        'faq_category': faq_category,
    })
