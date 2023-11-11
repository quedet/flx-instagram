import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ['submit'];

    /**
     *
     * @param {Event} event
     */
    submitable(event) {
        const value = event.target.value;
        const submitBtn = this.submitTarget;
        if (value.trim() !== '') {
            submitBtn.classList.remove('is--disabled');
            submitBtn.removeAttribute('disabled');
        } else {
            submitBtn.classList.add('is--disabled');
            submitBtn.setAttribute('disabled', true);
        }
    }
}