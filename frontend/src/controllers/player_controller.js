import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ['video', 'control'];
    connect() {
        const video = this.videoTarget;
        video.muted = true;
    }

    resume() {
        const video = this.videoTarget;
        const controls = this.controlTarget;

        if (video.paused) {
            video.play();
            controls.classList.add('hidden');
        } else {
            video.pause();
            controls.classList.remove('hidden');
        }
    }

    /**
     *
     * @param {Event} event
     */
    mute(event) {
        const mutedIcon = event.currentTarget.querySelector('svg.muted');
        const unmutedIcon = event.currentTarget.querySelector('svg.playing');
        const video = this.videoTarget;

        if (video.muted) {
            video.muted = false;
            mutedIcon.classList.add('hidden');
            unmutedIcon.classList.remove('hidden');
        } else {
            video.muted = true;
            unmutedIcon.classList.add('hidden');
            mutedIcon.classList.remove('hidden');
        }
    }
}