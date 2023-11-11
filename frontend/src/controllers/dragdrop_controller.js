import { Controller } from "@hotwired/stimulus";
import Cropper from "cropperjs";
import * as TurboDrive from "@hotwired/turbo";

export default class extends Controller {
    static targets = ['preview', 'submit', 'input'];

    connect() {
        this.file = null;
        this.fileChanged = false;
        this.initCropper();
    }

    /**
     *
     * @param {Event} event
     */
    changeImage(event) {
        let file = event.target.files[0];

        if (file) {
            this.file = file;
            this.fileChanged = true;
        } else {
            file = this.file;
            this.fileChanged = false;
        }

        const cropper = this.cropper;

        if (this.fileChanged) {
            const previewContainer = this.previewTarget;
            const previewImage = previewContainer.querySelector('img');
            const reader = new FileReader();
            reader.readAsDataURL(file);

            reader.onprogress = function (e) {
                console.log(e.loaded / e.total);
            };

            reader.onloadend = function () {
                console.log("Loaded");
                cropper.replace(reader.result);
                previewImage.setAttribute('src', reader.result);
            };
        }
    }

    initCropper() {
        if (this.hasPreviewTarget) {
            const img = this.previewTarget.querySelector('img');
            this.cropper = new Cropper(img, {
                aspectRatio: 1 / 1,
                background: true,
                viewMode: 2,
                autoCropArea: 1
            });
        }
    }

    /**
     *
     * @param {Event} event
     */
    upload(event) {
        event.preventDefault();

        const cropperData = this.cropper?.getData();
        const url = event.target.getAttribute('action');
        const type = this.file?.type;

        const form = new FormData(event.target);

        form.append('type', type);
        form.append('cropX', parseInt(cropperData.x));
        form.append('cropY', parseInt(cropperData.y));
        form.append('cropWidth', parseInt(cropperData.width));
        form.append('cropHeight', parseInt(cropperData.height));

        const xhr = new XMLHttpRequest();

        xhr.upload.onprogress = function (e) {
            console.log(e);
        };

        xhr.upload.onloadend = function () {
            console.log('Image uploaded');
        };

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                TurboDrive.visit(xhr.responseURL);
            }
        };

        xhr.open('POST', url, true);
        xhr.send(form);
    }
}