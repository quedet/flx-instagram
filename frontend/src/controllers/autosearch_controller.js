import {Controller} from "@hotwired/stimulus";
import debounce from "../helpers";
import * as TurboDrive from "@hotwired/turbo";
import Cookie from "js-cookie";


export default class extends Controller {
    static targets = ['renderer', 'form', 'input'];

    connect() {
        if (this.hasInputTarget) {
            this.inputTarget.addEventListener('input', this.onInputChange);
        }
    }

    disconnect() {
        if (this.hasInputTarget) {
            this.inputTarget.removeEventListener('input', this.onInputChange);
        }
    }

    /**
     *
     * @param {Event} event
     */
    search(event) {
        event.preventDefault();
        const form = new FormData(event.target);
        const url = event.target.getAttribute('action');
        const renderer = this.rendererTarget;

        // if (form.get('query').trim() !== '') {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', url, true);
            xhr.onreadystatechange = function () {
              if (xhr.readyState === 4 && xhr.status === 200) {
                  renderer.innerHTML = xhr.responseText;
              }
            };
            xhr.setRequestHeader('X-CSRFToken', Cookie.get('csrftoken'));
            xhr.send(form);
        // }
    }

    onInputChange = debounce(() => {
        this.formTarget.requestSubmit();
    }, 500);

    choose(event) {

        TurboDrive.visit(event.currentTarget.dataset.url);
    }
}