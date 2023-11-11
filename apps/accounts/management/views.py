import http

from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
import cv2, time, os
from django.conf import settings
from django.shortcuts import reverse
from apps.accounts.forms import EditProfileForm
from apps.accounts.models import Photo, Profile


class EditProfileView(LoginRequiredMixin, FormView):
    template_name = 'pages/account/manage/profile.html'
    form_class = EditProfileForm

    def get_success_url(self):
        return reverse('accounts:manage:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': Profile.objects.get(user=self.request.user)
        })
        return kwargs

    def form_valid(self, form):
        Profile.objects.filter(user=self.request.user).update(**form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = http.HTTPStatus.UNPROCESSABLE_ENTITY
        return response


class EditProfilePictureView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/manage/picture.html'

    def post(self, request, *args, **kwargs):
        uploaded_photo = request.FILES.get('photo')
        uploaded_photo_type = request.POST.get('type')

        cropX = int(request.POST.get('cropX', 0))
        cropY = int(request.POST.get('cropY', 0))
        cropWidth = int(request.POST.get('cropWidth', 50))
        cropHeight = int(request.POST.get('cropHeight', 50))

        if uploaded_photo and uploaded_photo_type:
            type_split = str(uploaded_photo_type).split('/')
            extension = str(type_split[1]).lower()

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/profile')):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/profile'))

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/profile/temp')):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/profile/temp'))

            filename = f'{request.user.uid}.{extension}'
            temp_pathname = os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/profile/temp/{filename}')
            crop_pathname = os.path.join(settings.MEDIA_ROOT, f'{request.user.uid}/profile/{filename}')

            with open(temp_pathname, 'wb+') as original_photo:
                for chunk in uploaded_photo.chunks():
                    original_photo.write(chunk)

            photo, created = Photo.objects.get_or_create(user=request.user)
            photo.original = f'{request.user.uid}/profile/temp/{filename}'

            if uploaded_photo_type != photo.type:
                photo.type = uploaded_photo_type

            if cropX != photo.cropX or cropY != photo.cropY or cropWidth != photo.width or cropHeight != photo.height:
                image = cv2.imread(photo.original.path)
                cropped_image = image[cropY:cropY + cropHeight, cropX:cropX + cropWidth]
                cv2.imwrite(crop_pathname, cropped_image)

                photo.cropped = f'{request.user.uid}/profile/{filename}'

                photo.cropX = cropX
                photo.cropY = cropY
                photo.width = cropWidth
                photo.height = cropHeight

            photo.save()

            # return HttpResponseRedirect(reverse('accounts:manage:profile'))
        else:
            photo = Photo.objects.get(user=request.user)
            extension = str(photo.original.name).split('.')[-1]

            if cropX != photo.cropX or cropY != photo.cropY or cropWidth != photo.width or cropHeight != photo.height:
                image = cv2.imread(photo.original.path)
                cropped_image = image[cropY:cropY + cropHeight, cropX:cropX + cropWidth]
                cv2.imwrite(photo.cropped.path, cropped_image)
                photo.cropped = f'{request.user.uid}/profile/{photo.user.uid}.{extension}'
                photo.save()

        return HttpResponseRedirect(reverse('accounts:manage:profile'))
