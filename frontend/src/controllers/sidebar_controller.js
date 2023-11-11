import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ['close', 'sidebarContent'];
    static values = {
        url: String,
    };

    toggle(e) {
        const dataset = e.currentTarget.dataset;
        this.urlValue = dataset.url;
        this.loadContent();

        this.element.classList.toggle('is--extended');
        document.body.classList.toggle('no--scroll');
    }

    open(e) {
        const dataset = e.currentTarget.dataset;
        this.urlValue = dataset.url;
        this.loadContent();
        this.element.classList.add('is--extended');
        document.body.classList.add('no--scroll');
    }

    close() {
        if (this.hasSidebarContentTarget) {
            const frame = this.sidebarContentTarget;
            frame.innerHTML = '';
        }
        this.element.classList.remove('is--extended');
        document.body.classList.remove('no--scroll');
    }


    loadContent() {
        if (this.hasSidebarContentTarget) {
            const frame = this.sidebarContentTarget;
            let reloadFlag = false;

            if (frame.src === this.urlValue) {
                reloadFlag = true;
            }

            frame.src = this.urlValue;

            if (reloadFlag) {
                frame.reload();
            }
        }
    }
}