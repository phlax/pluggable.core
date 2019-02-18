
import React from 'react';
import PropTypes from 'prop-types';
import exact from 'prop-types-exact';

// make dynamic!
import '@pluggable/core/bootstrap.min.css';


export class Http404 extends React.PureComponent {

    render () {
        // this needs to actually redirect to a page that will serve a 404 status coed

        return 'You 404ed!';
    }
}


export default class Layout extends React.Component {
    static propTypes = exact({
	active: PropTypes.object.isRequired,
        debug: PropTypes.func.isRequired,
	history: PropTypes.object.isRequired,
	log: PropTypes.func.isRequired,
        manager: PropTypes.object.isRequired,		
	signals: PropTypes.object.isRequired,
	widgets: PropTypes.object.isRequired,

	loaded: PropTypes.bool.isRequired,
        fetched: PropTypes.func,

        offsetX: PropTypes.number,
        offsetY: PropTypes.number,
        defaultApp: PropTypes.string
    });
    static defaultProps = {
        loaded: false,
        offsetX: 10,
        offsetY: 10,
	defaultApp: 'twitter'
    }
    supportedLanguages = ['en', 'fr']

    constructor (props) {
	super(props);
	const {signals, manager} = this.props;
	const {windows} = manager;	
        this.windows = windows;
	this.state = {
            active: null,
	    windows: []};
	// move to listening hoc
	signals.listen('auth.login.success',  this.onLogin, 'widget:layout');
	signals.listen('auth.register.success',  this.onLogin, 'widget:layout');
	signals.listen('auth.logout.success',  this.onLogout, 'widget:layout');
	signals.listen('ui.window.open',  this.openWindow, 'widget:layout');
	signals.listen('ui.window.close',  this.closeWindow, 'widget:layout');
	signals.listen('ui.window.focus',  this.focusWindow, 'widget:layout');
	// thse can probs all be unified to some kind of onPageReloadRequired
	signals.listen('ui.app.switch',  this.onAppSwitch, 'widget:layout');
	signals.listen('ui.page.switch',  this.onPageSwitch, 'widget:layout');	
	signals.listen('auth.login.oauth',  this.onOAuthLogin, 'widget:layout');
    }

    onOAuthLogin = async (redirect) => {
	this.setState({connectOAuth: redirect});
    }

    async componentWillMount () {
        this.props.log('layout mounting');
        const {active, loaded} = this.props;

	if (loaded && !active.app) {
	    // throw new 404()
	    this.setState({errors: '404'});
	}

        // const active = active.app || apps[defaultApp];
        this.setState({active});
    }

    async componentDidMount () {
        this.props.log('layout created');
    }

    onAppSwitch = (signal, active) => {
	const {active: appActive, history} = this.props;
	appActive.app = active;
	// or traverse to it??
	appActive.page = '';
	history.push('/' + active.route);
	this.setState({active});
    }

    onPageSwitch = (signal) => {
	const {active} = this.props;
	this.setState({active});
    }
    
    openWindow = (signal, window) => {
	const {widgets} = this.props;
	const {icon, title, widget} = window;
	const Window = widgets[widget];
	const props = {title, icon};
	this.windows.create({Window, window, props});
	const {stack, windows} = this.windows;
        this.setState({stack, windows});
    }

    closeWindow = (signal, window) => {
	this.windows.destroy(window);
	const {stack, windows} = this.windows;
        this.setState({stack, windows});
    }

    onClose = (evt) => {
        this.closeWindow(null, evt.currentTarget.name);
    }

    focusWindow = (signal, windowid) => {
	this.windows.focus(windowid);
	const {stack, windows} = this.windows;
        this.setState({stack, windows});
    }

    onLogin = (signal, user) => {
        const {active} = this.props;
	this.setState({active});
    }

    onLogout = (signal, user) => {
        const {active, signals} = this.props;
	signals.emit('ui.app.loading');	
	this.setState({active});
    }

    renderWindows () {
	const {windows} = this.state;
        return (
            <div>
              {windows.map((w, i) => {
                  const {Window} = w;
                  return <Window key={i} id={w.id} />;
              })}
            </div>);
    }

    renderWrongWay () {
	const {widgets} = this.props;
	const {'error.http4xx': Http4xx} = widgets;
	return <Http4xx />;
    }

    render () {
	const {errors} = this.state;
	const {active, fetched, loaded, widgets} = this.props;
	const {
	    'app': AppWidget,
	    'toolbar2': ToolbarWidget2} = widgets;
        const {user, app, page} = active;

	if (errors || typeof active.page !== 'string') {
            return this.renderWrongWay();
	}

	if (active.app) {
	    const {permission} = active.app;
	    if (permission && !active.user) {
                return this.renderWrongWay();
	    }	    
	    this.props.log('checking app permission', active.app.permission);
	}
	const extra = {}
	if (user) {
	    extra.user = user;
	}
	if (app) {
	    extra.app = app;
	}
	if (page) {
	    extra.page = page;
	}	
	if (fetched) {
	    extra.fetched = fetched;
	}
	if (loaded) {
	    extra.loaded = loaded;
	}
        return (
	    <div>
	      <ToolbarWidget2 {...extra} />
              <div id="app">
                <div className="p-3">
	          <AppWidget {...extra} />
                </div>
              </div>
              {this.renderWindows()}
            </div>);
    }
}
