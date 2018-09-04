from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string

from accounts.forms import ImageUploadForm
from accounts.models import RewardHistory

from sharespot.forms import SeatImgUploadForm
from sharespot.models import Division, Place, Space, Block, Seat, SeatImg, Series, Ticket, Emotion, EventReview, SeatReview, ShareInfoCategory, ShareInfo, ShareInfoImg, ShareInfoComment, TalkTopic, Talk

import datetime
import json
import urllib.request


def robots(request):
    return render(request, 'sharespot/robots.txt')


def sitemap(request):
    return render(request, 'sharespot/sitemap.xml')


def main(request):
    divisions = Division.objects.all()
    places = Place.objects.all()

    now = datetime.datetime.now()
    # series_all = Series.objects.filter(end__gte=now).order_by('start')
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
        series_pk = request.POST.get('series')
        series = Series.objects.get(pk=series_pk)
        event_date = request.POST.get('date')
        event_time = request.POST.get('time')
        event = series.event_set.get(start=event_date+' '+event_time)
        total_star = request.POST.get('rating_series')
        event_content = request.POST.get('event_comment')
        get_emotion_set = request.POST.get('emotion_set')

        if event_content != "":
            event_reward = RewardHistory.objects.create(
                user=user,
                reason="{} 리뷰글 작성".format(series.name),
                amount=5,
            )
        else:
            event_reward = None

        emotion_set = get_emotion_set.split(',')

        space_pk = request.POST.get('space')
        space = Space.objects.get(pk=space_pk)
        block_name = request.POST.get('block')
        block = Block.objects.get(section__space=space, name=block_name)

        all_seat = Seat.objects.none()

        for level in series.seatlevel_set.all():
            all_seat |= level.seat_set.all()

        seat_pk = request.POST.get('seat')

        seat = all_seat.get(block=block, pk=seat_pk)

        view_star = request.POST.get('rating_view')
        real_star = request.POST.get('rating_real')
        seat_content = request.POST.get('seat_comment')

        if seat_content != "":
            seat_reward = RewardHistory.objects.create(
                user=user,
                reason="{} {} 리뷰글 작성".format(space.name, seat),
                amount=5,
            )
        else:
            seat_reward = None

        # anony_name = request.POST.get('anony_name').exists()

        ticket = Ticket.objects.create(user=user)

        event_review = EventReview.objects.create(
            ticket=ticket,
            history=event_reward,
            event=event,
            total_star=total_star,
            content=event_content,
        )

        seat_review = SeatReview.objects.create(
            ticket=ticket,
            history=seat_reward,
            seat=seat,
            view_star=view_star,
            real_star=real_star,
            content=seat_content,
        )

        event_review.save()
        seat_review.save()

        for item in emotion_set:
            if item != '':
                emotion = Emotion.objects.get(name=item.strip())
                event_review.emotion_set.add(emotion)

        event_review.save()
        seat_review.save()

        form = SeatImgUploadForm(request.POST, request.FILES)

        if form.is_valid():
            seat_img1 = SeatImg.objects.create(
                seat=seat,
                user=user,
                history=seat_reward,
                review=seat_review,
                img=form.cleaned_data['image1'],
                status=request.POST.get('img_option1'),
            )
            seat_img1.history = RewardHistory.objects.create(
                user=user,
                reason="{} {} 좌석뷰 등록".format(space.name, seat),
                amount=10,
            )
            seat_img1.save()

            if form.cleaned_data['image2']:
                seat_img2 = SeatImg.objects.create(
                    seat=seat,
                    user=user,
                    history=seat_reward,
                    review=seat_review,
                    img=form.cleaned_data['image2'],
                    status=request.POST.get('img_option2'),
                )
                seat_img2.save()

            if form.cleaned_data['image3']:
                seat_img3 = SeatImg.objects.create(
                    seat=seat,
                    user=user,
                    history=seat_reward,
                    review=seat_review,
                    img=form.cleaned_data['image3'],
                    status=request.POST.get('img_option3'),
                )
                seat_img3.save()

        # if anony_name.exists():
        #     event_review.nick_name = anony_name
        #     seat_review.nick_name = anony_name
        #     event_review.save()
        #     seat_review.save()

        return redirect(request.GET.get('next', '/'))

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


def get_date_list(request):
    series_pk = request.GET.get('series_pk')
    series = Series.objects.get(pk=series_pk)
    data = series.event_set \
        .extra(select={'datestr': "to_char(start, 'YYYY-MM-DD')"}) \
        .values_list('datestr', flat=True) \
        .distinct()

    html = render_to_string('sharespot/option_list.html', {
        'request': request,
        'object_list': data,
    })

    space = series.space
    blocks = Block.objects.filter(section__space=space) \
        .values_list('name', flat=True) \
        .distinct()

    block_html = render_to_string('sharespot/option_list.html', {
        'request': request,
        'object_list': blocks,
    })

    return JsonResponse({
        'html': html,
        'space': space.name,
        'space_pk': space.pk,
        'block_html': block_html
    })


def get_time_list(request):
    series_pk = request.GET.get('series_pk')
    series = Series.objects.get(pk=series_pk)
    series_date = request.GET.get('series_date')
    data = series.event_set.filter(start__date=series_date) \
        .extra(select={'datestr': "to_char(start, 'HH24:MI')"}) \
        .values_list('datestr', flat=True) \
        .distinct()

    html = render_to_string('sharespot/option_list.html', {
        'request': request,
        'object_list': data,
    })
    return JsonResponse({
        'html': html,
    })


def get_seat_list(request):
    series_pk = request.GET.get('series_pk')
    series = Series.objects.get(pk=series_pk)

    space = request.GET.get('space')
    space = Space.objects.get(pk=space)
    block = request.GET.get('block')
    block = Block.objects.get(section__space=space, name=block)

    all_seat = Seat.objects.none()

    for level in series.seatlevel_set.all():
        all_seat |= level.seat_set.filter(block=block)

    data = all_seat.distinct()

    html = render_to_string('sharespot/option_list.html', {
        'request': request,
        'object_list': data,
    })
    return JsonResponse({
        'html': html,
    })


def review_thanks(request):
    user = request.user
    review_pk = request.POST.get('review')

    if 'seat' in request.POST:
        review = SeatReview.objects.get(pk=review_pk)
    elif 'event' in request.POST:
        review = EventReview.objects.get(pk=review_pk)
    else:
        pass

    review.say_thank(user)

    return HttpResponse(review.count_thanked())


def space_like(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)

    if request.method == 'POST':
        space.toggle_like(user)
        return HttpResponse('complete')
    return render(request)


def place_basic(request, space):
    # TODO: 날씨
    space = Space.objects.get(en_name=space)
    place = space.place

    return render(request, 'sharespot/place_basic.html', {
        'place': place,
        'space': space,
    })


@login_required
def place_space(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)
    place = space.place
    if 'series' in request.GET:
        close_series = Series.objects.get(en_name=request.GET['series'])
    else:
        close_series = space.get_close_series()
    reviews = space.get_space_review().filter(is_confirmed=True)

    return render(request, 'sharespot/place_space.html', {
        'user': user,
        'place': place,
        'space': space,
        'close_series': close_series,
        'reviews': reviews,
    })


def place_space_block(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)

    if request.method == 'POST':
        block_pk = request.POST.get('pk')
        block = Block.objects.get(pk=block_pk)
        series_pk = request.POST.get('series_pk')
        series = Series.objects.get(pk=series_pk)
        all_seat = Seat.objects.none()

        for level in series.seatlevel_set.all():
            all_seat |= level.seat_set.all()

        all_seat = all_seat.all().filter(block=block)

        html = render_to_string('sharespot/place_space_block.html', {
            'request': request,
            'space': space,
            'block': block,
            'all_seat': all_seat,
        })

        reviews = block.get_block_review().filter(is_confirmed=True)

        info_html = render_to_string('sharespot/place_space_block_info.html', {
            'request': request,
            'user': user,
            'block': block,
            'reviews': reviews,
        })

        return JsonResponse({
            'html': html,
            'info_html': info_html,
        })
    return render(request)


def place_space_seat(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)

    if request.method == 'POST':
        seat_pk = request.POST.get('pk')
        seat = Seat.objects.get(pk=seat_pk)
        reviews = SeatReview.objects.filter(seat=seat)

        html = render_to_string('sharespot/place_space_seat.html', {
            'request': request,
            'user': user,
            'seat': seat,
            'reviews': reviews,
        })

        return JsonResponse({
            'html': html,
        })
    return render(request)


@login_required
def place_share(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)
    place = space.place
    share_info = ShareInfo.objects.filter(place=place)
    share_category = ShareInfoCategory.objects.all()

    if request.method == 'POST':
        category = request.POST.get('category')
        category = ShareInfoCategory.objects.get(pk=category)
        name = request.POST.get('q')
        address = request.POST.get('address')
        lat_lon = request.POST.get('lat_lon')
        content = request.POST.get('content')

        info = ShareInfo.objects.create(
            user=user,
            place=place,
            category=category,
            name=name,
            address=address,
            lat_lon=lat_lon,
            content=content,
        )

        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            img = form.cleaned_data['image']
            ShareInfoImg.objects.create(info=info, img=img)

        return HttpResponseRedirect(request.path_info)

    return render(request, 'sharespot/place_share.html', {
        'user': user,
        'place': place,
        'space': space,
        'share_category': share_category,
        'share_info': share_info,
    })


def place_share_edit(request, space):
    if request.method == 'POST':
        info_pk = request.POST.get('info_pk')
        new_content = request.POST.get('new_content')

        info = get_object_or_404(ShareInfo, pk=info_pk)
        info.content = new_content
        info.save()

        return HttpResponse(info.content)
    return render(request)


def place_share_delete(request, space):
    if request.method == 'POST':
        info_pk = request.POST.get('info_pk')

        info = get_object_or_404(ShareInfo, pk=info_pk)
        info.delete()

        return JsonResponse({
            'info_pk': info_pk,
        })


def place_share_comment_create(request, space):
    user = request.user
    space = Space.objects.get(en_name=space)

    if request.method == 'POST':
        info_pk = request.POST.get('info_pk')
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
            'space': space,
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
        info = comment.share_info

        comment.delete()
        info_comment_count = info.shareinfocomment_set.count()

        return JsonResponse({
            'comment_pk': comment_pk,
            'info_comment_count': info_comment_count,
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
    now = datetime.datetime.now()
    if 'place' in request.GET:
        place = Place.objects.get(en_name=request.GET['place'])
        series_all = Series.objects.filter(space__place=place, end__gte=now).order_by('start')
    elif 'division' in request.GET:
        division = Division.objects.get(en_name=request.GET['division'])
        series_all = Series.objects.filter(division=division, end__gte=now).order_by('start')
    else:
        series_all = Series.objects.filter().order_by('start')

    return render(request, 'sharespot/series_list.html', {
        'divisions': divisions,
        'series_all': series_all,
    })


def series_like(request, series):
    user = request.user
    series = Series.objects.get(en_name=series)

    if request.method == 'POST':
        series.toggle_like(user)
        return HttpResponse('complete')
    return render(request)


def series_basic(request, series):
    series = Series.objects.get(en_name=series)

    return render(request, 'sharespot/series_basic.html', {
        'series': series,
    })


def series_review(request, series):
    series = Series.objects.get(en_name=series)
    reviews = EventReview.objects.filter(event__series=series, is_confirmed=True)

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
