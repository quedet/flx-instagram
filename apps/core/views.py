import mimetypes
import os
import time, cv2

import moviepy.editor
from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse

from django.shortcuts import redirect, reverse, get_object_or_404
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramWordSimilarity
from django.contrib.contenttypes.models import ContentType

from django.core.files.base import ContentFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from apps.assets.models import Media, Image, Video, Story
from apps.messenger.models import Room, Message
from apps.accounts.models import User, SearchHistory

from moviepy.editor import VideoFileClip
from PIL import Image as PILImage
from io import BytesIO


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/home.html'

    def get(self, request, *args, **kwargs):
        medias = Media.objects.filter(owner__followers__in=[request.user])
        return self.render_to_response({
            'page': 'home',
            'medias': medias
        })


class PostDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/details.html'

    def get(self, request, *args, **kwargs):
        media = get_object_or_404(Media, id=kwargs['post_id'])
        return self.render_to_response({
            'post': media
        })


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/search/index.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'page': 'search',
            'accounts': request.user.search_history.requested_users.all()
        })


class SearchResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/search/results.html'

    def post(self, request, *args, **kwargs):
        query = request.POST.get('query', None)

        if query and str(query).strip() != '':
            results = User.objects.exclude(username='AnonymousUser').annotate(similarity=TrigramWordSimilarity(query, 'username') + TrigramWordSimilarity(query, 'first_name') + TrigramWordSimilarity(query, 'last_name'))\
                .filter(similarity__gt=0.3).order_by('-similarity')
            is_recent_active = False
        else:
            results = request.user.search_history.requested_users.all()
            is_recent_active = True

        return self.render_to_response({
            'page': 'search',
            'is_recent_active': is_recent_active,
            'accounts': results,
        })


class ExploreView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/explore.html'

    def get(self, request, *args, **kwargs):
        medias = Media.objects.all()

        return self.render_to_response({
            'page': 'explore',
            'medias': medias
        })


class ReelsRedirectionView(LoginRequiredMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        reel = Media.objects.filter(content_type=ContentType.objects.get_for_model(Video)).first()
        return redirect(reverse('core:reels-details', args=[reel.id]))


class ReelsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/reels.html'

    def get(self, request, *args, **kwargs):
        reel_id = kwargs.get('reel_id', None)
        reels = Media.objects.filter(content_type=ContentType.objects.get_for_model(Video))
        reels_list = list(reels.values_list('id', flat=True))

        page = reels_list.index(int(reel_id)) + 1

        paginator = Paginator(reels, 1)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            page_obj = paginator.page(1)

        next_url = None
        next_page_object = None
        previous_url = None
        previous_page_object = None

        if page_obj.has_next():
            next_page_number = page_obj.next_page_number()
            next_page_object = reels_list[next_page_number - 1]
            next_url = reverse('core:reels-details', args=[next_page_object])

        if page_obj.has_previous():
            previous_page_number = page_obj.previous_page_number()
            previous_page_object = reels_list[previous_page_number - 1]
            previous_url = reverse('core:reels-details', args=[previous_page_object])

        reel = page_obj.object_list[0] if page_obj.object_list else None

        if reel:
            reel.total_views = reel.total_views + 1
            reel.save()

        print(reel.total_views)

        return self.render_to_response({
            'reel': reel,
            'next_url': next_url,
            'previous_id': previous_page_object,
            'next_id': next_page_object,
            'previous_url': previous_url,
            'stories_count': paginator.num_pages,
            'stories_range': reels_list
        })


class MessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/messenger.html'

    def get(self, request, *args, **kwargs):

        return self.render_to_response({
            'page': 'messages',
            'rooms': Room.objects.filter(users_subscribed__in=[request.user])
        })


class NotificationsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/home.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'page': 'notifications'
        })


class CreateView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/create.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'page': 'create'
        })

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type', None)
        description = request.POST.get('description', None)
        uploaded_file = request.FILES.get('media', None)

        split_type = str(type).split('/')
        mimeType = split_type[0]
        extension = split_type[1]

        if uploaded_file and mimeType in ['image', 'video']:
            current_time = time.time()
            filename = "".join(str(current_time).split('.')) + '.' + extension
            file_path = os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/assets/{filename}')

            obj = None

            with open(file_path, 'wb+') as file:
                for chunk in uploaded_file.chunks():
                    file.write(chunk)

            if mimeType == 'image':
                img = cv2.imread(file_path)
                height, width = img.shape[:2]

                obj = Image(owner=request.user, type=type, width=width, height=height)
                obj.source = f'{request.user.uid}/assets/{filename}'
                obj.save()

            elif mimeType == 'video':
                vcap = cv2.VideoCapture(file_path)
                width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                obj = Video(owner=request.user, type=type, width=width, height=height)
                obj.source = f'{request.user.uid}/assets/{filename}'
                obj.save()

                video = VideoFileClip(file_path)

                frame_data = video.get_frame(2)
                img = PILImage.fromarray(frame_data, 'RGB')
                temp_thumb = BytesIO()

                img.save(temp_thumb, "JPEG")
                temp_thumb.seek(0)

                obj.thumbnail.save(f"{obj.source.name}.jpeg", ContentFile(temp_thumb.read()),
                                        save=True)
                temp_thumb.close()


            else:
                return HttpResponseBadRequest()

            Media.objects.create(item=obj, owner=request.user, mime_type=mimeType, description=description)

            return HttpResponseRedirect(reverse('core:home'))
        else:
            return HttpResponseBadRequest()


class CreatStoryView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/story.html'

    def post(self, request, *args, **kwargs):
        uploaded_file_type = request.POST.get('type', None)
        description = request.POST.get('description', None)
        uploaded_file = request.FILES.get('media', None)
        t_start = int(request.POST.get('minValue', 0))
        t_end = int(request.POST.get('maxValue', 60))

        # Retrieve the cropped data from the frontend
        cropX = request.POST.get('cropX', None)
        cropY = request.POST.get('cropY', None)
        cropWidth = request.POST.get('cropWidth', None)
        cropHeight = request.POST.get('cropHeight', None)

        # Check either or not the file and his type has been submitted in the request
        if uploaded_file and uploaded_file_type:
            # Retrieve the file mime type
            type_split = str(uploaded_file_type).split('/')
            mimeType = type_split[0]
            extension = type_split[1].lower()

            # Set temp file name based on current timestamp
            current_time = time.time()
            filename = "".join(str(current_time).split('.')) + '.' + extension

            if mimeType == 'image':
                story = None

                if not cropX and not cropY:
                    story = Story.objects.create(user=request.user, thumbnail=uploaded_file,
                                                 description=description)
                else:
                    # Check if the temp file's folder exists, otherwise create one
                    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/temp')):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/temp'))

                    temp_file_path = os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/temp/{filename}')
                    storage_file_path = os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/thumbnails/{filename}')

                    # Save the uploaded file
                    with open(temp_file_path, 'wb+') as temp_file:
                        for chunk in uploaded_file.chunks():
                            temp_file.write(chunk)

                    if os.path.isfile(temp_file_path):
                        cropX = int(cropX)
                        cropY = int(cropY)
                        cropWidth = int(cropWidth)
                        cropHeight = int(cropHeight)

                        file = cv2.imread(temp_file_path)
                        file_cropped = file[cropY:cropY + cropHeight, cropX:cropX + cropWidth]
                        cv2.imwrite(storage_file_path, file_cropped)

                        os.remove(temp_file_path)

                        story = Story.objects.create(user=request.user, description=description)
                        story.thumbnail = f'{request.user.uid}/stories/thumbnails/{filename}'
                        story.save()

                if story.thumbnail and not story.video:
                    img = cv2.imread(story.thumbnail.path)
                    height, width, layers = img.shape
                    size = (width, height)
                    duration_in_seconds = 30
                    fps = 1
                    filename = "".join(str(current_time).split('.')) + '.mp4'
                    path = os.path.join(settings.MEDIA_ROOT, f'{story.user.uid}/stories/{filename}')

                    out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

                    for _ in range(int(fps * duration_in_seconds)):
                        out.write(img)
                    out.release()

                    story.video = f'{story.user.uid}/stories/{filename}'
                    story.save()

                return HttpResponseRedirect(reverse('accounts:profile:posts', args=[request.user.username]))

            if mimeType == 'video':
                # Check if the temp file's folder exists, otherwise create one
                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/temp')):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/temp'))

                temp_file_path = os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/stories/temp/{filename}')
                storage_file_path = os.path.join(settings.MEDIA_ROOT,
                                                 f'{request.user.uid}/stories/{filename}')

                with open(temp_file_path, 'wb+') as file:
                    for chunk in uploaded_file.chunks():
                        file.write(chunk)

                tape = VideoFileClip(temp_file_path)

                if int(tape.duration) > t_end:
                    subclip = tape.subclip(t_start, t_end)
                    subclip.write_videofile(storage_file_path)

                    story = Story(user=request.user, description=description)
                    story.video = f'{request.user.uid}/stories/{filename}'
                    story.save()
                else:
                    Story.objects.create(user=request.user, description=description, video=uploaded_file)

                tape.close()
                os.remove(temp_file_path)

                # vcap = cv2.VideoCapture(temp_file_path)
                #
                # # Get video properties -  frame width and
                # width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
                # height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # fps = vcap.get(cv2.CAP_PROP_FPS)
                # frames = vcap.get(cv2.CAP_PROP_FRAME_COUNT)

                # # Define the start and end frames fir the subclip
                # start_frame = int(t_start * fps)
                # end_frame = int(t_end * fps)
                #
                # # Output
                # fourcc = cv2.VideoWriter_fourcc(*f'mp4v')
                # out = cv2.VideoWriter(storage_file_path, fourcc, fps, (width, height))
                #
                # # set the frame position to the start frame
                # vcap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                #
                # # Read and write frames within the specified range
                # for i in range(start_frame, end_frame):
                #     ret, frame = vcap.read()
                #
                #     if not ret:
                #         break
                #
                #     out.write(frame)
                #
                # vcap.release()
                # out.release()
                # return HttpResponseRedirect(reverse('accounts:profile:posts', args=[request.user.username]))

        return HttpResponseBadRequest()


class UserStoryView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/stories.html'

    def get(self, request, *args, **kwargs):
        story_username = kwargs['user_name']
        story_id = kwargs['story_id']

        stories = Story.objects.filter(user__username=story_username)
        stories_list = list(stories.values_list('id', flat=True))

        page = stories_list.index(int(story_id)) + 1

        paginator = Paginator(stories, 1)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            page_obj = paginator.page(1)

        next_url = None
        next_page_object = None
        previous_url = None
        previous_page_object = None

        if page_obj.has_next():
            next_page_number = page_obj.next_page_number()
            next_page_object = stories_list[next_page_number - 1]
            next_url = reverse('core:stories', args=[story_username, next_page_object])

        if page_obj.has_previous():
            previous_page_number = page_obj.previous_page_number()
            previous_page_object = stories_list[previous_page_number - 1]
            previous_url = reverse('core:stories', args=[kwargs['user_name'], previous_page_object])

        story = page_obj.object_list[0] if page_obj.object_list else None

        if request.user != story.user and request.user not in story.viewed_by.all():
            story.viewed_by.add(request.user)

        return self.render_to_response({
            'story': story,
            'next_url': next_url,
            'previous_id': previous_page_object,
            'next_id': next_page_object,
            'previous_url': previous_url,
            'stories_count': paginator.num_pages,
            'stories_range': stories_list
        })


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/core/home.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'page': 'profile'
        })