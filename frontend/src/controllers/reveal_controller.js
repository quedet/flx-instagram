import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ['item', 'image'];

    connect() {
        const oberver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                const video = entry.target.querySelector('[data-player-target="video"]');
                const control = entry.target.querySelector('[data-player-target="control"]');
                const picture = entry.target.querySelector('[data-reveal-target="image"]');

                if (video) {
                    if (entry.isIntersecting) {
                        video.play();
                        control.classList.add('hidden');
                    } else {
                        video.pause();
                        control.classList.remove('hidden');
                    }
                }
                function loaded() {
                    picture.classList.add('loaded');
                }

                if (picture && entry.isIntersecting) {
                    const img = picture.querySelector('img');

                    if (img.complete) {
                        loaded();
                    } else {
                        img.addEventListener("load", loaded);
                    }
                }

            });
        }, {
            threshold: 0.4,
        });

        this.itemTargets.forEach(el => {
            oberver.observe(el);
        });
    }
}