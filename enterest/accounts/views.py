from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from sharespot.models import Series, Ticket, TalkTopic
from accounts.models import RewardHistory, Gift, GiftRequest, FAQCategory

import datetime


def signup(request):
    return render(request, 'accounts/signup.html')


def signup_info(request):
    return render(request, 'accounts/signup_info.html')


def login(request):
    return render(request, 'accounts/login.html')


@login_required
def myinfo(request):
    user = request.user

    if request.method == 'POST':
        new_pw1 = request.POST.get('new_password1')
        nick_name = request.POST.get('nick_name')
        email = request.POST.get('email')
        birth = request.POST.get('birth')
        phone = request.POST.get('phone')

        if new_pw1 != '':
            user.set_password(new_pw1)

        if nick_name != '':
            user.profile.nick_name = nick_name
        if email != '':
            user.email = email
        if birth != '':
            user.profile.phone = birth
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

    if request.method == 'GET':
        user = request.user
        old_pw = request.GET.get('old_password')
        if user.check_password(old_pw):
            return HttpResponse('match')
        else:
            return HttpResponse('mis_match')


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
    now = datetime.datetime.now()

    # 관심 appear들의 다가오는 이벤트를 한 쿼리셋으로 묶기; 방법이 구린거 같아서 추후 성능보고 좀더 고민 ㅠ.ㅠ
    appear_series = []
    for appear in user.liked_appear_set:
        appear_series += appear.event_set.filter(start__gte=now).values_list('series', flat=True)

    queryset = Series.objects.none()
    for series in list(set(appear_series))[:25]:
        queryset |= Series.objects.get(name=series)

    queryset = queryset.order_by('start')

    return render(request, 'accounts/mylike.html', {
        'user': user,
        'queryset': queryset,
    })


@login_required
def mywriting(request):
    user = request.user
    joined_topics = TalkTopic.objects.filter(is_joined=True)  # 에러각

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
        GiftRequest.objects.create(user=user, gift=gift)
        RewardHistory.objects.create(
            user=user,
            reason=gift.name + ' 교환',
            amount=gift.price*(-1),
        )

        # 유저 리워드 차감
        user.reward.use_point(gift.price)
        user.reward.save()

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
