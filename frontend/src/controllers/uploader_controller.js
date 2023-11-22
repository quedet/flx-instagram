import { Controller } from "@hotwired/stimulus";
import Cookie from "js-cookie";
import * as TurboDrive from "@hotwired/turbo";
import "cropperjs/dist/cropper.css";
import Cropper from "cropperjs";

export default class extends Controller {
    static targets = ['preview', 'select', 'progress', 'range', 'submit', 'image', 'video'];

    connect() {
        this.file = null;
        this.fileChanged = false;

        this.durationGap = 10;
    }

    setVolume() {
        if (this.hasPreviewTarget) {
            const preview = this.previewTarget;
            const video = preview.querySelector('video');

            if (video) {
                video.volume = 0.5;
            }
        }
    }

     /**
     *
     * @param {Event} event
     */
    play(event) {
        const target = event.currentTarget;

        if (target.paused) {
            if (Math.round(target.currentTime) >= this.maxValue) {
                target.currentTime = this.minValue;
            }
            target.play();
        } else {
            target.pause();
        }
    }


    /**
     *
     * @param {Event} event
     */
    initCropper(event) {
        const file = this.imageTarget;
        const target = event.currentTarget;
        const viewMode = target.dataset.viewMode || 1;

        this.cropper = new Cropper(file, {
            viewMode: viewMode,
            autoCrop: true,
            autoCropArea: 1,
            background: false,
            ready() {
                target.setAttribute('data-action', "click->uploader#cancelCropper");
                target.textContent = 'Cancel';
            }
        });
    }

    /**
     * @param {Event} event
     */
    cancelCropper(event) {
        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }

        const target = event.currentTarget;
        target.setAttribute('data-action', "click->uploader#initCropper");
        target.textContent = 'Edit';
    }

    /**
     *
     * @param {Event} event
     */
    update(event) {
        if (this.hasPreviewTarget) {
            const time = this.previewTarget.querySelector("#time");
            time.innerHTML = this.customTimeFormat(event.target.currentTime);
        }
    }

    /**
     *
     * @param {Event} event
     */
    upload(event) {
        let file = event.target.files[0];

        if (file) {
            this.file = file;
            this.fileChanged = true;
        } else {
            file = this.file;
            this.fileChanged = false;
        }

        if (this.fileChanged) {
            const mimeType = file.type.split('/')[0];
            const reader = new FileReader();
            reader.readAsDataURL(file);
            const preview = this.previewTarget;
            const select = this.selectTarget;
            const progressBar = this.progressTarget;
            const self = this;

            reader.onprogress = function (e) {
                let percent = (e.loaded / e.total) * 100;
                progressBar.style.width = percent + '%';
            };

            reader.onloadend = function () {
                if (mimeType === 'video') {
                    let media = new Audio(reader.result);

                    media.onloadedmetadata = function () {
                        select.classList.add('is--faded');
                        preview.classList.add('is--active');
                        progressBar.style.width = 0;

                        preview.innerHTML = `
                            <div class="upload--media">
                                <video autoplay data-uploader-target="video" data-action="click->uploader#play timeupdate->uploader#update">
                                    <source src="${reader.result}" type="${file.type}" />
                                </video>
                                <div class="video--duration">
                                    <div class="duration--timestamp"><span id="time">00:00</span>/<span>${self.customTimeFormat(media.duration)}</span></div>
                                </div>
                            </div>
                            <div class="upload--overview">
                                <textarea data-controller="textarea-autogrow"
                                      rows="1" placeholder="Write a quick overview of that video."
                                      class="upload--overview--input"
                                      name="description" id="id_description"
                                      data-textarea-autogrow-resize-debounce-delay-value="500"
                                ></textarea>
                            </div>
                            <div class="upload--actions">
                                <div class="action--left">
                                    <label for="id_media" class="text-blue-500 cursor-pointer">
                                        Change
                                    </label>
                                    <button type="button" data-action="click->uploader#initVideoCropper">Edit</button>
                                </div>
                                <div class="action-right">
                                    <button type="submit" 
                                        data-uploader-target="submit" 
                                        class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer"
                                    >Post it</button>
                                </div>
                            </div>    
                        `;

                        self.setVolume();
                    };
                }

                if (mimeType === 'image') {
                    select.classList.add('is--faded');
                    preview.classList.add('is--active');
                    progressBar.style.width = 0;

                    preview.innerHTML = `
                        <div class="upload--media">
                            <img class="object-center object-cover" data-uploader-target="image" src="${reader.result}" alt="${file.name}" />
                        </div>
                        <div class="upload--overview">
                            <textarea data-controller="textarea-autogrow"
                                  rows="1" placeholder="Write a quick caption for this image."
                                  class="upload--overview--input"
                                  name="description" id="id_description"
                                  data-textarea-autogrow-resize-debounce-delay-value="500"
                            ></textarea>
                        </div>
                        <div class="upload--actions">
                            <div class="action--left">
                                <label for="id_media" class="text-blue-500 cursor-pointer">
                                    Change
                                </label>
                                <button type="button" data-action="click->uploader#initCropper">Edit</button>
                            </div>
                            <div class="action-right">
                                <button type="submit" 
                                    data-uploader-target="submit" 
                                    class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer"
                                >Post it</button>
                            </div>
                        </div> 
                    `;
                }
            };
        }
    }

    /**
     * @param {Event} event
     */
    submit(event) {
        event.preventDefault();
        const url = event.target.getAttribute('action');
        const xhr = new XMLHttpRequest();
        const form = new FormData(event.target);

        if (this.cropper) {
            const crop = this.cropper.getData();
            form.append('cropX', parseInt(crop.x));
            form.append('cropY', parseInt(crop.y));
            form.append('cropWidth', parseInt(crop.width));
            form.append('cropHeight', parseInt(crop.height));
        }

        form.append('type', this.file?.type);

        const submitBtn = this.submitTarget;
        const csrftoken = Cookie.get('csrftoken');

        xhr.upload.onprogress = function (e) {
            let percent = (e.loaded / e.total) * 100;
            submitBtn.setAttribute('disabled', true);
            submitBtn.innerHTML = `${percent}%`;
        };

        xhr.upload.onloadend = function () {
            submitBtn.removeAttribute('disabled');
            submitBtn.innerHTML = `Uploaded`;
        };

        xhr.onreadystatechange = function () {
          if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                  submitBtn.innerHTML = 'Redirecting...';
                  TurboDrive.visit(xhr.responseURL);
              } else {
                  submitBtn.innerHTML = 'Sorry';
              }
          }
        };

        xhr.open('POST', url, true);
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
        xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
        xhr.send(form);
    }

    /**
     *
     * @param seconds
     * @param guide
     * @return {string}
     */
    customTimeFormat(seconds, guide) {
        seconds = seconds < 0 ? 0 : seconds;
        let s = Math.floor(seconds % 60);
        let m = Math.floor(seconds / 60 % 60);
        let h = Math.floor(seconds / 3600);
        let gm = Math.floor(guide / 60 % 60);
        let gh = Math.floor(guide / 3600); // handle invalid times

        if (isNaN(seconds) || seconds === Infinity) {
            // '-' is false for all relational operators (e.g. <, >=) so this setting
            // will add the minimum number of fields specified by the guide
            h = m = s = '-';

            return h + ':' + s;
        } // Check if we need to show hours


        h = h > 0 || gh > 0 ? h + ':' : ''; // If hours are showing, we may need to add a leading zero.
        // Always show at least one digit of minutes.

        m = ((h || gm >= 10) && m < 10 ? '0' + m : m) + ':'; // Check if leading zero is need for seconds

        h = parseInt(h) < 10 ? '0' + h : h;
        s = parseInt(s) < 10 ? '0' + s : s;

        return h + m + s;
    }
}