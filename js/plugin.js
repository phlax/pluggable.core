
import LocalizedStrings from 'react-localization';

import ShareableWorker from '@pluggable/sharedworker/shared';
import {Session} from '@pluggable/web-app/managers/auth';

import {Logger, Signals} from '@pluggable/app/utils';
import {appConfig} from './config';
import Plugin from '@pluggable/web-app/plugin';


export default class CorePlugin extends Plugin {
    languages = ['en', 'fr'];
    hasL10n = true;
    defaultApp = 'twitter';
    appConfig = appConfig;

    constructor (app) {
	super(app);
	this.app.defaultApp = this.defaultApp;
    }

    get name () {
        return 'core';
    }

    addHooks = (hooks) => {
	hooks.i18n.tap("core.i18n", this.i18n);
	hooks.worker.tapPromise("core.worker", this.worker);
	hooks.signals.tap("core.signals", this.getSignals);
	hooks.logger.tap("core.logger", this.getLogger);
	hooks.crypto.tap("core.crypto", this.crypto);
	hooks.buttons.tapPromise("core.buttons", this.buttons);
	hooks.exporters.tapPromise("core.exporters", this.exporters);
	this.log('plugin hooks added');
    }

    crypto = () => {
        return new Crypto();
    }

    getLogger = () => {
	return new Logger(m => this.app.signals.emit('core.logger', m))
    }

    getSignals = () => {
        return new Signals(this.app.debug('app:signals'));
    }

    i18n = () => {
	return LocalizedStrings;
    }

    get logger () {
	return this.app.logger;
    }

    updateL10n = (signal, data) => {
	const log = this.app.debug('app:loader')
	const {l10n} = this.app;
	log('received l10n', data);
	const current = l10n.getContent();
	for (let lang of Object.keys(data)) {
	    current[lang] = Object.assign({}, current[lang] || {}, data[lang])
	}
	l10n.setContent(current);
	log('added l10n to env')
    }

    updateSettings = (signal, data) => {
	// console.log('updating settings in ui', data);
    }

    preLoad = async () => {
	this.app.signals.listen('l10n.update', this.updateL10n);
	this.app.signals.listen('settings.update', this.updateSettings);
    }

    session = async (result) => {
        let session = new Session(this.app);
	result['auth.authenticate'] = session.authenticate;
	result['auth.register'] = session.register;
	result['auth.onlogin'] = session.onLogin;
	result['auth.onsignup'] = session.onSignup;
    }

    worker = async () => {
	this.app.worker = new ShareableWorker(this.app, 'worker.foo');
	await this.app.worker.connect();
    }

    loadL10n = async (language, filetype) => {
	return import('@pluggable/core/locales/' + language + '/' + filetype + '.json');
    }
}
