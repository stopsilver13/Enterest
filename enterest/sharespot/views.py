from django.db.models import Q
from django.shortcuts import render

from sharespot.models import Division, Place, Space, Series, Ticket, Emotion, EventReview, SeatReview, ShareInfoCategory, ShareInfo, TalkTopic, Talk

import datetime


def main(request):
    divisions = Division.objects.all()
    places = Place.objects.all()
    series_all = Series.objects.all()

    return render(request, 'sharespot/main.html', {
        'divisions': divisions,
        'places': places,
        'series_all': series_all,
    })


def register_review(request):  # ?ticket_id=
    # 리뷰 수정시
    if 'ticket_id' in request.GET:
        ticket_id = request.GET['ticket_id']
        ticket = Ticket.objects.get(id=ticket_id)

    # 새 리뷰 작성시
    else:
        ticket = None

    if request.method == 'POST':
        # TODO: 이미지 저장, 이미지/리뷰 리워드 지급
        user = request.user
        event = request.POST.get('event')  # 추후수정
        seat = request.POST.get('seat')  # 추후수정
        total_star = request.POST.get('total_star')
        view_star = request.POST.get('view_star')
        real_star = request.POST.get('real_star')
        anony_name = request.POST.get('anony_name').exists()

        picked_emotions = request.POST.get('emotions').split(',')  # 추후수정; 문자열로 받아서 split 할 계획

        ticket_exist = Ticket.objects.get(user=user, event_review__event=event).exists()

        if ticket_exist:
            ticket = Ticket.objects.get(user=user, event_review__event=event)
            # TODO: ticket 정보 업데이트
        else:
            ticket = Ticket.objects.create(user=user)
            event_review = EventReview.objects.create(
                ticket=ticket,
                event=event,
                total_star=total_star,
            )
            for item in picked_emotions:
                emotion = Emotion.objects.get(name=item)
                event_review.emotion_set.add(emotion)

            event_review.save()

            seat_review = SeatReview.objects.create(
                ticket=ticket,
                seat=seat,
                view_star=view_star,
                real_star=real_star,
            )

            if anony_name.exists():  # 입력 닉네임 여부에 따라 리뷰 닉네임 여부 결정
                event_review.nick_name = anony_name
                seat_review.nick_name = anony_name
                event_review.save()
                seat_review.save()

    series_all = Series.objects.all()
    emotions = Emotion.objects.all()

    return render(request, 'sharespot/register_review.html', {
        'ticket': ticket,
        'series_all': series_all,
        'emotions': emotions,
    })

# 공연/경기가 입력되면 그 시리즈의 날짜 set과 해당 장소+그 장소의 블럭 받아오는 ajax
# 공연/경기날짜가 입력되면 해당 공연과 시간 set 받아오는 ajax
# 블럭 선택하면 그 블럭의 좌석 받아오는 ajax


def place_basic(request, space):
    # TODO: 날씨
    space = Space.objects.get(en_name=space)
    place = space.place

    return render(request, 'sharespot/place_basic.html', {
        'place': place,
        'space': space,
    })


def place_space(request, space):
    space = Space.objects.get(en_name=space)
    place = space.place
    now = datetime.datetime.now()
    if Series.objects.get(Q(start__lte=now, end__gte=now)).exists():
        close_series = Series.objects.get(Q(start__gte=now, end__lte=now))
    else:
        close_series = Series.objects.filter(start__gte=now).order_by('start').first()

    return render(request, 'sharespot/place_space.html', {
        'place': place,
        'space': space,
        'close_series': close_series,
    })


def place_share(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)
    place = space.place
    share_info = ShareInfo.objects.filter(place=place)
    share_category = ShareInfoCategory.objects.all()

    # TODO: if request.method == 'POST':

    return render(request, 'sharespot/place_share.html', {
        'user': user,
        'place': place,
        'space': space,
        'share_category': share_category,
        'share_info': share_info,
    })

# 정보글 수정/삭제 ajax
# 댓글 입력/수정/삭제 ajax


def series_list(request):  # ?division= ?place=
    # TODO: 필터링 방식에 따라 변동 가능성 있음
    if 'place' in request.GET:
        place = Place.objects.get(en_name=request.GET['place'])
        series_all = Series.objects.filter(space__place=place)
    elif 'division' in request.GET:
        division = Division.objects.get(en_name=request.GET['division'])
        series_all = Series.objects.filter(division=division)
    else:
        series_all = Series.objects.all()

    return render(request, 'sharespot/series_list.html', {
        'series_all': series_all,
    })


def series_basic(request, series):
    series = Series.objects.get(en_name=series)

    return render(request, 'sharespot/series_basic.html', {
        'series': series,
    })


def series_review(request, series):
    series = Series.objects.get(en_name=series)
    reviews = EventReview.objects.filter(event__series=series)

    emotions = Emotion.objects.annotate(quote_time=eventreview_set.filter(event__series=series).count()).order_by('-quote_time')  # 흠... 아마 에러날듯

    return render(request, 'sharespot/series_review.html', {
        'series': series,
        'reviews': reviews,
        'emotions': emotions,
    })


def series_talk_list(request, series):
    series = Series.objects.get(en_name=series)
    topics = TalkTopic.objects.filter(series=series)
    talks = Talk.objects.filter(topic__series=series)  # 몇개까지 보여줄 것? 페이지네이션? 더보기?

    return render(request, 'sharespot/series_talk_list.html', {
        'series': series,
        'topics': topics,
        'talks': talks,
    })


def series_talk(request, series, topic):
    topic = TalkTopic.objects.get(pk=topic)
    topics = TalkTopic.objects.filter(series=series)
    talks = Talk.objects.filter(topic=topic)  # 몇개까지 보여줄 것? 페이지네이션? 더보기?

    return render(request, 'sharespot/series_talk.html', {
        'topic': topic,
        'topics': topics,
        'talks': talks,
    })

# 이야깃거리 생성/수정/(삭제) ajax
# 이야기 생성/수정/삭제 ajax
# 각 행동에 대해 페이지 리로딩 여부는 생각을 해봐야 할듯















