// This is the scss entry file
import "../styles/index.scss";
import "@hotwired/turbo";

import { Application } from "@hotwired/stimulus";
import { definitionsFromContext } from "@hotwired/stimulus-webpack-helpers";
import ReadMore from 'stimulus-read-more';
import TextareaAutogrow from 'stimulus-textarea-autogrow';
import CharacterCounter from 'stimulus-character-counter';
import { Dropdown, Popover } from "tailwindcss-stimulus-components";

window.Stimulus = Application.start();
const context = require.context("../controllers", true, /\.js$/);
window.Stimulus.load(definitionsFromContext(context));

window.Stimulus.register('read-more', ReadMore);
window.Stimulus.register('textarea-autogrow', TextareaAutogrow);
window.Stimulus.register('character-counter', CharacterCounter);
window.Stimulus.register('popover', Popover);
window.Stimulus.register('dropdown', Dropdown);
