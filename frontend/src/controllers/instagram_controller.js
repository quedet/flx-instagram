import { Controller } from "@hotwired/stimulus";
import { connectStreamSource, disconnectStreamSource } from "@hotwired/turbo";
import ReconnectingWebsocket from "reconnecting-websocket";

export default class extends Controller {
    static values = {
        socketUrl: String,
    };

    connect() {
        const ws_url = this.socketUrlValue;
        this.source = new ReconnectingWebsocket((window.location.protocol === ':https' ? 'wss': 'ws') + '://' + window.location.host + ws_url);
        connectStreamSource(this.source);
    }

    disconnect() {
        if (this.source) {
            disconnectStreamSource(this.source);
            this.source.close();
            this.source = null;
        }
    }

    /**
     * Send Data to socket
     * @param {WebSocket} websocket
     * @param {Object} data
     */
    sendData(websocket, data) {
       websocket.send(JSON.stringify(data));
    }

    /**
     * Comment video or photo
     * @param {Event} event
     */
    comment(event) {
        event.preventDefault();
        const form = new FormData(event.target);
        const data = {
            action: 'comment a post',
            data: {
                post_id: form.get('id'),
                post_type: form.get('type'),
                comment: form.get('comment')
            }
        };
        this.sendData(this.source, data);
    }

    /**
     *
     * @param {Event} event
     */
    like(event) {
        const dataset = event.currentTarget.dataset;
        const data = {
            action: 'like a post',
            data: {
                post_id: dataset.id,
                post_type: dataset.type
            }
        };

        this.sendData(this.source, data);
    }

     /**
     *
     * @param {Event} event
     */
    bookmark(event) {
        const dataset = event.currentTarget.dataset;
        const data = {
            action: 'bookmark a post',
            data: {
                post_id: dataset.id,
                post_type: dataset.type
            }
        };

        this.sendData(this.source, data);
    }

    /**
     *
     * @param {Event} event
     */
    follow(event) {
        const data = {
            action: 'follow a user',
            data: {
                user_uid: event.currentTarget.dataset.id
            }
        };

        this.sendData(this.source, data);
    }

    searchHistory(event) {
        const data = {
            action: 'save into search history',
            data: {
                account_uid: event.currentTarget.dataset.uid,
            }
        };

        this.sendData(this.source, data);
    }

    deleteItemFormSearchHistory(event) {
        const data = {
            action: "delete search history item",
            data: {
                account_username: event.currentTarget.dataset.username,
            }
        };

        this.sendData(this.source, data);
    }

    /**
     *
     * @param {Event} event
     */
    sendMessage(event) {
        event.preventDefault();
        const form = new FormData(event.target);

        const data = {
            action: 'send message',
            data: {
                message: form.get('message')
            }
        };
        this.sendData(this.source, data);
    }
}