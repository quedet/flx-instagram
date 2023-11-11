import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ['username', 'input', 'email'];

    connect() {
        this.user_name = {
            first_name: '',
            last_name: ''
        };
        this.email = '';
        this.password = '';
    }

    /**
     *
     * @param {Event} event
     */
    setUsername(event) {
        const target = event.target;
        const name = target.name;
        const value = target.value.trim().toLowerCase();
        this.user_name[name] = value.split(' ').join('_');

        let username = '';

        if (this.user_name.first_name !== '' && this.user_name.last_name !== '') {
            username = [this.user_name.first_name, this.user_name.last_name].join('_');
        } else if (this.user_name.first_name === '') {
            username = this.user_name.last_name;
        } else {
            username = this.user_name.first_name;
        }

        this.usernameTarget.setAttribute('value', username);
    }

    /**
     *
     * @param {Event} event
     */
    check(event) {
        console.log(event);
    }

    checkEmail(event) {
        const patterns = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        const value = event.target.value.trim();
        // const re = new RegExp(patterns);
        if (value.match(patterns) !== null || value === '') {
            this.emailTarget.classList.remove('error');
        } else {
            this.emailTarget.classList.add('error');
        }
    }

    checkPassword(event) {
        console.log(event);
    }
}