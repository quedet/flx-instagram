import { Controller } from "@hotwired/stimulus";
import Cookie from "js-cookie";
import * as TurboDrive from "@hotwired/turbo";


export default class extends Controller {
    static targets = ['preview', 'select', 'progress', 'submit'];

    connect() {
        this.file = null;
        this.fileChanged = false;
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

            reader.onprogress = function (e) {
                let percent = (e.loaded / e.total) * 100;
                // progressBar.classList.remove('hidden');
                progressBar.style.width = percent + '%';
            };

            reader.onloadend = function () {
                select.classList.add('is--faded');
                preview.classList.add('is--active');
                progressBar.style.width = 0;

                if (mimeType === 'video') {
                    preview.innerHTML = `
                        <div class="upload--media">
                            <video autoplay>
                                <source src="${reader.result}" type="${file.type}" />
                            </video>
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
                                    data-uploader-target="submit" 
                                    class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer"
                            >Save</button>
                        </div>    
                    `;
                }
                if (mimeType === 'image') {
                    preview.innerHTML = `
                        <div class="upload--media">
                            <img class="object-center object-cover" src="${reader.result}" alt="${file.name}" />
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
                            <label for="id_media" class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer">
                                Change
                            </label>
                            <button type="submit" 
                                    data-uploader-target="submit" 
                                    class="bg-blue-500 text-white px-3 py-2 rounded-md cursor-pointer"
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
}