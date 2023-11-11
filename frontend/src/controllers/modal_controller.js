import { Modal } from "tailwindcss-stimulus-components";

export default class extends Modal {
    static targets = [...Modal.targets, ...['modalContent']];
    static values = {
        ...Modal.values,
        ...{
            url: {
                type: String,
                required: false,
            }
        }
    };

    open(e) {
        const dataset = e.currentTarget.dataset;
        this.urlValue = dataset.url;
        if (dataset.page) {
            this.element.classList.add(dataset.page);
        }
        this.loadContent();
        super.open(e);
    }

    close(e) {
        if (this.hasModalContentTarget) {
            const frame = this.modalContentTarget;
            frame.innerHTML = '';
        }
        super.close(e);
    }

    loadContent() {
        if (this.hasModalContentTarget && this.hasUrlValue) {
            const frame = this.modalContentTarget;

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