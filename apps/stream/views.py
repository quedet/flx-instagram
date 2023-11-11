import re, os
from django.conf import settings as django_settings
from django.views.generic import View

from . import settings
from .utils.log_services import log_watch_request, get_request_ip
from .utils.stream_services import get_streaming_response


# Create your views here.
class VideoStreamingView(View):
    def get(self, request, *args, **kwargs):
        """get range header & create streaming response"""
        # initialize parameters
        max_load_volume = settings.STREAM_MAX_LOAD_VOLUME
        path_key = settings.STREAM_DEFAULT_VIDEO_PATH_URL_VAR
        range_re_pattern = settings.STREAM_RANGE_HEADER_REGEX_PATTERN
        log_enabled = settings.STREAM_WATCH_LOG_ENABLED
        media_dir = django_settings.MEDIA_ROOT
        media_url = django_settings.MEDIA_URL

        # get video path & range header
        video_path = request.GET.get(path_key)
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_re = re.compile(range_re_pattern, re.I)
        video_path = video_path.replace(media_url, str(media_dir) + '/')
        video_path = os.path.join(django_settings.BASE_DIR, video_path)

        # log
        if log_enabled:
            ip = get_request_ip(request)
            log_watch_request(video_path, request.user.is_authenticated, ip, request.user)

        # create response
        response = get_streaming_response(
            path=video_path,
            range_header=range_header,
            range_re=range_re,
            max_load_volume=max_load_volume,  # the maximum volume of the response body
        )

        return response
