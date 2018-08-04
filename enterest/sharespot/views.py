from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from sharespot.models import Division, Place, Space, Series, Ticket, Emotion, EventReview, SeatReview, ShareInfoCategory, ShareInfo, ShareInfoComment, TalkTopic, Talk

import json
import urllib.request


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
    close_series = space.get_close_series()

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


# ajax 노노
def place_share_create(request, series, topic):
    user = request.user
    series = Series.objects.get(en_name=series)
    topic = TalkTopic.objects.get(pk=topic)

    if request.method == 'POST':
        content = request.POST.get('content')

        info = ShareInfo.objects.create(
            user=user,
            place=series.space.place,
            category=category,
            name=name,
            address=address,
            lat_lon=lat_lon,
            content=content,
        )

        html = render_to_string('sharespot/talk.html', {
            'request': request,
            'series': series,
            'topic': topic,
            'talk': talk,
        })

        return JsonResponse({
            'html': html,
        })
    return render(request)


def place_share_edit(request, series, topic):
    if request.method == 'POST':
        talk_pk = request.POST.get('talk_pk')
        new_content = request.POST.get('new_content')

        talk = get_object_or_404(Talk, pk=talk_pk)
        talk.content = new_content
        talk.save()

        return HttpResponse(talk.content)
    return render(request)


def place_share_delete(request, series, topic):
    if request.method == 'POST':
        talk_pk = request.POST.get('talk_pk')
        print(talk_pk)

        talk = get_object_or_404(Talk, pk=talk_pk)
        talk.delete()

        return JsonResponse({
            'talk_pk': talk_pk,
        })


def place_share_comment_create(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)

    if request.method == 'POST':
        info_pk = request.POST.get('info_pk')
        print(info_pk)
        info = ShareInfo.objects.get(pk=info_pk)
        anony_name = request.POST.get('anony')
        content = request.POST.get('content')

        info_comment = ShareInfoComment.objects.create(
            user=user,
            anony_name=anony_name,
            share_info=info,
            content=content,
        )

        html = render_to_string('sharespot/place_share_info_comment.html', {
            'request': request,
            'comment': info_comment,
        })

        info_comment_count = info.shareinfocomment_set.count()

        return JsonResponse({
            'html': html,
            'info_comment_count': info_comment_count,
        })
    return render(request)


def place_share_comment_edit(request, space):
    if request.method == 'POST':
        comment_pk = request.POST.get('comment_pk')
        new_content = request.POST.get('new_content')

        comment = get_object_or_404(ShareInfoComment, pk=comment_pk)
        comment.content = new_content
        comment.save()

        return HttpResponse(comment.content)
    return render(request)


def place_share_comment_delete(request, space):
    if request.method == 'POST':
        comment_pk = request.POST.get('comment_pk')

        comment = get_object_or_404(ShareInfoComment, pk=comment_pk)
        comment.delete()

        return JsonResponse({
            'comment_pk': comment_pk,
        })


def place_share_search(request, space):
    config_secret = json.loads(open(settings.CONFIG_SETTINGS_COMMON_FILE).read())
    client_id = config_secret['naver']['client_id']
    client_secret = config_secret['naver']['client_secret']

    if request.method == 'GET':
        q = request.GET.get('q')
        encText = urllib.parse.quote("{}".format(q))
        url = "https://openapi.naver.com/v1/search/local?query=" + encText  # json 결과
        local_api_request = urllib.request.Request(url)
        local_api_request.add_header("X-Naver-Client-Id", client_id)
        local_api_request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(local_api_request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            result = json.loads(response_body.decode('utf-8'))
            items = result.get('items')

            return JsonResponse({
                'items': items,
            })
        return HttpResponse(404)
    return render(request)

# 정보글 수정/삭제 ajax
# 댓글 입력/수정/삭제 ajax


def series_list(request):
    # TODO: 필터링 방식에 따라 변동 가능성 있음
    divisions = Division.objects.all().order_by('pk')
    if 'place' in request.GET:
        place = Place.objects.get(en_name=request.GET['place'])
        series_all = Series.objects.filter(space__place=place)
    elif 'division' in request.GET:
        division = Division.objects.get(en_name=request.GET['division'])
        series_all = Series.objects.filter(division=division)
    else:
        series_all = Series.objects.all()

    return render(request, 'sharespot/series_list.html', {
        'divisions': divisions,
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

    return render(request, 'sharespot/series_review.html', {
        'series': series,
        'reviews': reviews,
    })


def series_talk_list(request, series):
    user = request.user
    series = Series.objects.get(en_name=series)
    topics = TalkTopic.objects.filter(series=series)
    talks = Talk.objects.filter(topic__series=series).order_by('-pk')  # 몇개까지 보여줄 것? 페이지네이션? 더보기?

    if request.method == 'POST':
        content = request.POST.get('topic_content')
        explain = request.POST.get('topic_explain')

        TalkTopic.objects.create(
            user=user,
            series=series,
            content=content,
            explain=explain,
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'sharespot/series_talk_list.html', {
        'user': user,
        'series': series,
        'topics': topics,
        'talks': talks,
    })


def series_talk(request, series, topic):
    user = request.user
    series = Series.objects.get(en_name=series)
    topic = TalkTopic.objects.get(pk=topic)
    topics = TalkTopic.objects.filter(series=series)
    talks = Talk.objects.filter(topic=topic).order_by('pk')  # 몇개까지 보여줄 것? 페이지네이션? 더보기?

    if request.method == 'POST':
        content = request.POST.get('topic_content')
        explain = request.POST.get('topic_explain')

        TalkTopic.objects.create(
            user=user,
            series=series,
            content=content,
            explain=explain,
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'sharespot/series_talk.html', {
        'user': user,
        'series': series,
        'topic': topic,
        'topics': topics,
        'talks': talks,
    })


def series_talk_create(request, series, topic):
    user = request.user
    series = Series.objects.get(en_name=series)
    topic = TalkTopic.objects.get(pk=topic)

    if request.method == 'POST':
        anony_name = request.POST.get('anony_name')
        content = request.POST.get('content')

        talk = Talk.objects.create(
            user=user,
            anony_name=anony_name,
            topic=topic,
            content=content,
        )

        html = render_to_string('sharespot/talk.html', {
            'request': request,
            'series': series,
            'topic': topic,
            'talk': talk,
        })

        return JsonResponse({
            'html': html,
        })
    return render(request)


def series_talk_edit(request, series, topic):
    if request.method == 'POST':
        talk_pk = request.POST.get('talk_pk')
        new_content = request.POST.get('new_content')

        talk = get_object_or_404(Talk, pk=talk_pk)
        talk.content = new_content
        talk.save()

        return HttpResponse(talk.content)
    return render(request)


def series_talk_delete(request, series, topic):
    if request.method == 'POST':
        talk_pk = request.POST.get('talk_pk')

        talk = get_object_or_404(Talk, pk=talk_pk)
        talk.delete()

        return JsonResponse({
            'talk_pk': talk_pk,
        })


# 각 행동에 대해 페이지 리로딩 여부는 생각을 해봐야 할듯
