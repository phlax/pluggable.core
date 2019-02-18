
import {
    appsIcon, connectedIcon, disconnectedIcon, stoppedIcon,
    logoutIcon, runningIcon, wrongWayImage} from './images';

// managers
import {
    Applications, Layout,
    LoginNoAccount, LoginSuccess, SignupAccountAlready,
    SignupSuccess, OAuthProvider, OAuthProviders} from './ui';
import {UsernameValidator, EmailValidator} from './validators';
import {RegisterAction, LoginAction} from './actions';

import {appConfig as webAppConfig} from '@pluggable/web-app/config';


export const appConfig = {};

appConfig.columns = {...webAppConfig.columns}
appConfig.managers = {...webAppConfig.managers}
appConfig.settings = {...webAppConfig.settings}
appConfig.utils = {...webAppConfig.utils}
appConfig.widgets = {
    'layout': {
	component: Layout,
	fetches: {
	    status: 'worker.status'
	},
	props: [
	    'active',
	    'debug',
	    'defaultApp',
	    'history',
	    'log',
	    'manager',
	    'signals',
	    'widgets']},

    // auth
    'auth.signup.aside': {
	component: SignupAccountAlready,
	listens: ['auth.panels.close'],
	props: ['l10n', 'widgets']},
    'auth.signup.oauth': {
	component: OAuthProviders,
	listens: ['auth.panels.close'],
	props: [
	    'oauth',
	    'l10n',
	    'widgets']},
    'auth.signup.oauth.provider': {
	component: OAuthProvider,
	props: ['server', 'widgets']},
    'auth.login.aside': {
	component: LoginNoAccount,
	listens: ['auth.panels.close'],
	props: ['widgets']},
    'auth.login.success': {
	component: LoginSuccess,
	props: ['l10n', 'widgets']},
    'auth.register.success': {
	component: SignupSuccess,
	props: [
	    'l10n',
	    'signals',
	    'widgets']},
}

appConfig.buttons = {
    "core.button.logout": {
        weight: 1,
	title: "titleLogout",
	icon: "icon.logout",
	context: "core.toolbar",
	emits: 'auth.logout',
	props: ['active'],
	condition: (props => {
	    return Boolean(props.active.user)
	}),
    },
    "button.password.reset": {
	title: "buttonLabelPasswordReset",
	color: "link",
	size: 'xl',
	emits: 'auth.password.reset'}
}

appConfig.panels = {
    'auth.login': {
	widget: 'flex',
	panels: {
	    'main': {
		widget: 'auth.login.main',
		className: 'panel-auth-login-main',
	    },
	    'aside': {
		widget: 'auth.login.aside',
	    }
	}
    },

    'auth.login.main': {
	panels: {
	    'login': {
		widget: 'form.auth.login',
	    },
	    'hr': {
		widget: 'hr',
	    },
	    'forgotten': {
		widget: 'button.password.reset',
	    },
	}
    },

    'auth.signup': {
	widget: 'flex',
	panels: {
	    'main': {
		widget: 'auth.signup.main',
		className: 'panel-auth-signup-main',
	    },
	    'aside': {
		widget: 'auth.signup.aside',
	    }
	}
    },

    'auth.signup.main': {
	panels: {
	    'signup': {
		widget: 'form.auth.signup',
	    },
	    'providers': {
		widget: 'auth.signup.oauth',
	    },
	}
    },
}

appConfig.media = {
    'icon.apps': {
	src: appsIcon,
	alt: 'altApplications'},
    'icon.logout': {
	src: logoutIcon,
	alt: 'altLogout'},
    'icon.running': {
	src: runningIcon,
	alt: 'altRunning'},
    'icon.connected': {
	src: connectedIcon,
	alt: 'altConnected'},
    'icon.stopped': {
	src: stoppedIcon,
	alt: 'altStopped'},
    'icon.disconnected': {
	src: disconnectedIcon,
	alt: 'altDisconnected'},
    'image.wrong.way': {
	src: wrongWayImage,
	alt: 'altWrongWay'}}


appConfig.windows = {
    'window.applications': {
	title: 'windowTitleApplications',
	icon: 'icon.apps',
	component: Applications,
	props: [
	    'active',
	    'apps',
	    'signals',
	    'widgets']},
}


appConfig.forms = {
    'form.auth.signup': {
	action: 'auth.register',
	submit: 'buttonLabelRegister',
	onsuccess: 'auth.register.success',
	parts: {
	    email: {
		validators: ['core.email'],
		submit: 'buttonLabelNext',
		emits: ['auth.panels.close'],
		fields: {
		    'email': {
			widget: 'field.email',
			label: 'fieldLabelEmail',
			placeholder: 'placeholderEnterAnEmail',
			size: 'lg'
		    }},
	    },
	    username: {
		fields: {
		    'username': {
			widget: 'field.username',
			size: 'lg'
		    }},
	    },
	    password: {
		fields: {
		    'password': {
			widget: 'field.password',
			size: 'lg'
		    }},
	    }
	},
    },
    'form.auth.login': {
	action: 'auth.login',
	submit: 'buttonLabelSignin',
	onsuccess: 'auth.login.success',
	fields: {
	    'field.username': {
		widget: 'field.username',
		size: 'lg'
	    },
	    'field.password': {
		widget: 'field.password',
		size: 'lg'
	    }},
    }
}

appConfig.validators = {
    'core.email': EmailValidator,
    'core.username': UsernameValidator,
}

appConfig.actions = {
    'auth.register': RegisterAction,
    'auth.login': LoginAction,
}
