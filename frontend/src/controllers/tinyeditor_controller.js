import { Controller } from "@hotwired/stimulus";
import Cookie from "js-cookie";
import * as TurboDrive from "@hotwired/turbo";
import "cropperjs/dist/cropper.css";
import Cropper from "cropperjs";

export default class extends Controller {
    static targets = ['preview', 'video', 'select', 'progress', 'range', 'submit', 'file'];
    static values = {
        min: {
            type: Number,
            default: 0
        },
        max: {
            type: Number,
            default: 60
        }
    };

    connect() {
        this.file = null;
        this.fileChanged = false;
        this.durationGap = 10;
    }

    playing(event) {
        const video = event.currentTarget;
        const canvas = this.fileTarget;
        let ctx = canvas.getContext('2d');

        (function loop() {
            ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, canvas.width, canvas.height); // , 0, 0, canvas.width, canvas.height
            setTimeout(loop, 1000 / 30);
        })();
    }

    /**
     *
     * @param {Event} event
     */
    initCropper(event) {
        const file = this.fileTarget;
        const target = event.currentTarget;
        const viewMode = target.dataset.viewMode || 1;

        this.cropper = new Cropper(file, {
            aspectRatio: 9 / 16,
            viewMode: viewMode,
            autoCrop: true,
            autoCropArea: 1,
            background: false,
            ready() {
                target.setAttribute('data-action', "click->tinyeditor#cancelCropper");
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
        target.setAttribute('data-action', "click->tinyeditor#initCropper");
        target.textContent = 'Edit';
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

        const mimeType = file.type.split('/')[0];
        const reader = new FileReader();

        const preview = this.previewTarget;
        const select = this.selectTarget;
        const progressBar = this.progressTarget;
        const self = this;


        if (this.fileChanged) {
            reader.readAsDataURL(file);

            reader.onprogress = function (e) {
                let percent = (e.loaded / e.total) * 100;
                progressBar.style.width = percent + '%';
            };

            reader.onloadend = function () {
                select.classList.add('is--faded');
                preview.classList.add('is--active');
                progressBar.style.width = 0;
                self.result = reader.result;

                if (mimeType === 'video') {
                    preview.innerHTML = `Loading...`;
                    let media = new Audio(reader.result);

                    media.onloadedmetadata = function () {
                        let duration = Math.round(media.duration);

                        if (duration < 60) {
                            self.maxValue = duration;
                        }

                        const right = 100 - (self.maxValue / duration) * 100 + '%';

                        preview.innerHTML = `
                            <div class="upload--media">
                                <video autoplay data-tinyeditor-target="video" data-action="click->tinyeditor#play timeupdate->tinyeditor#update play->tinyeditor#playing">
                                    <source src="${reader.result}" type="${file.type}" />
                                </video>
                            </div>
                            <div class="upload--controls">
                                <div class="video--duration">
                                    <div class="duration--timestamp"><div>00:00</div><div>${self.customTimeFormat(media.duration)}</div></div>
                                </div>
                                <div class="video--slider">
                                    <div class="range--progress" data-tinyeditor-target="range" style="right: ${right}"></div>
                                    <div class="range--input">
                                        <input type="range" name="minValue" data-action="input->tinyeditor#range" class="min--val" min="${self.minValue}" max="${duration}" value="0" />
                                        <input type="range" name="maxValue" data-action="input->tinyeditor#range" class="max--val" min="${self.minValue}" max="${duration}" value="${self.maxValue}" />
                                    </div>
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
                                <label for="id_media" class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer">
                                    Change
                                </label>
                                <button type="submit" 
                                        data-tinyeditor-target="submit" 
                                        class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer"
                                >Save</button>
                            </div>
                        `;


                    };
                }

                if (mimeType === 'image') {
                    preview.innerHTML = `
                        <div class="upload--media">
                            <img id="upload--media--image" data-tinyeditor-target="file" src="${reader.result}" alt="${file.name}" />
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
                            <label for="id_media" class="text-blue-500 px-3 py-2 cursor-pointer">
                                Change
                            </label>
                           <button type="button" data-action="click->tinyeditor#initCropper">Edit</button>
                            <button type="submit" 
                                    data-tinyeditor-target="submit" 
                                    class="text-blue-500 px-3 py-2 rounded-md cursor-pointer"
                            >Save</button>
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
        const fileType = this.file?.type;
        const splitType = fileType.split('/');

        if (splitType[0] === 'image' && this.cropper) {
            const crop = this.cropper.getData();
            form.append('cropX', parseInt(crop.x));
            form.append('cropY', parseInt(crop.y));
            form.append('cropWidth', parseInt(crop.width));
            form.append('cropHeight', parseInt(crop.height));
        }

        form.append('type', fileType);

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
     * @param {Event} event
     */
    update(event) {
        if (Math.round(event.target.currentTime) >= this.maxValue) {
            event.target.pause();
        }
    }

    /**
     * Update Video Current Time
     * @param {Event} event
     */
    range(event) {
        const target = event.currentTarget;
        const name = target.getAttribute('name');
        this[name] = parseInt(target.value);
        const video = this.videoTarget;
        const progress = this.rangeTarget;

        if (this.maxValue - this.minValue < this.durationGap) {
            if (name === 'minValue') {
                target.value = this.maxValue - this.durationGap;
            } else {
                target.value = this.minValue + this.durationGap;
            }
            console.log(target.value);
        } else {
            progress.style.left = (this.minValue / parseInt(target.getAttribute('max'))) * 100 + '%';
            progress.style.right = 100 - (this.maxValue / parseInt(target.getAttribute('max'))) * 100 + '%';
        }

        if (name === 'minValue') {
            video.currentTime = this.minValue;
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