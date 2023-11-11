import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ['progress', 'video', 'play'];

    connect() {
        this.play();
        this.setVolume();
    }

    disconnect() {
        if (this.hasVideoTarget) {
            this.videoTarget.pause();
        }
    }

    togglePlay() {
        const video = this.videoTarget;

        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    }

    setVolume() {
        this.videoTarget.volume = 0.5;
    }
    handleVolume(event) {
        const video = this.videoTarget;
        video.volume = parseInt(event.currentTarget.value) / 100;
    }

    pause() {
        if (this.hasVideoTarget)
            this.videoTarget.pause();
    }

    play() {
        if (this.hasVideoTarget)
            this.videoTarget.play();
    }

    playing() {
        this.playTarget.innerHTML = `<svg aria-label="Pause" class="x1lliihq x1n2onr6 x9bdzbf" fill="currentColor" height="16" role="img" viewBox="0 0 48 48" width="16"><title>Pause</title><path d="M15 1c-3.3 0-6 1.3-6 3v40c0 1.7 2.7 3 6 3s6-1.3 6-3V4c0-1.7-2.7-3-6-3zm18 0c-3.3 0-6 1.3-6 3v40c0 1.7 2.7 3 6 3s6-1.3 6-3V4c0-1.7-2.7-3-6-3z"></path></svg>`;
    }

    stopped() {
        this.playTarget.innerHTML = `<svg aria-label="Play" class="x1lliihq x1n2onr6 x9bdzbf" fill="currentColor" height="16" role="img" viewBox="0 0 24 24" width="16"><title>Play</title><path d="M5.888 22.5a3.46 3.46 0 0 1-1.721-.46l-.003-.002a3.451 3.451 0 0 1-1.72-2.982V4.943a3.445 3.445 0 0 1 5.163-2.987l12.226 7.059a3.444 3.444 0 0 1-.001 5.967l-12.22 7.056a3.462 3.462 0 0 1-1.724.462Z"></path></svg>`;
    }

    timing(event) {
        const progress = this.progressTarget;
        const filled = progress.querySelector('#progress__filled');

        const video = event.currentTarget;
        const percent = (video.currentTime / video.duration) * 100;

        filled.style.width = percent + '%';
    }
}