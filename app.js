'use strict';
/*jslint node: true */
/*jslint esversion: 6  */
/* globals $: true */
/* eqeqeq: false */
/* -W041: false */
const type = require('type-of');
const request = require('superagent');
const h = require('hyperscript-string');
const $ = require('domtastic');
const rivets = require('rivets');

$.fn.clear = function() {
  this.forEach((e) => {
    e.innerHTML = '';
  });
  return this;
};

$.fn.outerHTML = function() {
  return this.prop('outerHTML');
};

const state = {
  message: '',
  knowledge: [],
  conversation: [],
  error: false
};

function _error(method, url, { response: res }) {
  res = res ? [res.status, res.text] : [];
  console.warn(`[${method} ${url}]`, ...res);
}

function send_message(text='', cb) {
  request.post('/message').send(text).then(({ body }) => {
    state.conversation.push({ text: body });
  }, (e) => { 
    _error('POST', '/message', e);
    cb && cb();
  });
}

send_message();

$('.Conversation-input')
  .on('keydown', (e) => {
    let message = state.message;
    if (e.code == 'Enter' && !e.shiftKey && !e.altKey && !e.ctrlKey) {
      if (message == '')
        return;
      state.message = '';
      state.conversation.push({ text: message.split(/\s*[\n\r]+\s*/g), is_user: true });
      send_message(message, () => { 
        state.error = true; 
      });
      return false;
    }
  })
  .on('paste', (e) => {
    e.preventDefault();
    let text = e.clipboardData.getData("text/plain");
    document.execCommand("insertHTML", false, text);
    return false;
  });

function _const(self, key, value) {
  Object.defineProperty(self, key, {
    value, writable: false, enumerable: true, configurable: true
  });
  return self;
}

const { Binding } = rivets._;
rivets._.Binding = class extends Binding {
  parseTarget() {
    if (this.binder.parseTarget) {
      Object.assign(this, this.binder.parseTarget(this.keypath));
    }
    return super.parseTarget();
  }

  publish() {
    _const(this, 'state', 'publish');
    let ret = super.publish();
    _const(this, 'state');
  }
};

rivets.binders['input'] = {
  parseTarget(keypath) {
    let empty_class;
    [keypath, empty_class] = keypath.trim().split(/\s*\?\s*/);
    return { keypath, empty_class };
  },

  bind: function(el) {
    this._empty = true;
    $(el).on('input.rv-input', this.publish);
    this._watch = () => {
      el.innerHTML = '';
      if (el.innerHTML == '') {
        clearInterval(this._watcher);
      }
    };
  },

  unbind: function(el) {
    $(el).off('.rv-input');
    clearInterval(this._watcher);
  },

  routine: function(el, value) {
    if (this.state != 'publish') {
      clearInterval(this._watcher);
      el.innerText = value;
    }
    state.error = false;
    this._empty = value == '';
    if (this._empty) {
      this._watcher = setInterval(this._watch, 30);
    }
    if (this.empty_class) {
      $(el).toggleClass(this.empty_class, this._empty);
    }
  },

  getValue : function(el) {
    return el.innerText.trim();
  }
};

global.$state = state;

rivets.bind(document.body, state);
