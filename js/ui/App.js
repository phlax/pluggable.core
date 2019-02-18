import React from 'react';
import exact from 'prop-types-exact';

import PluggableWebApp from '@pluggable/web-app/app';
import {PluginWrapper} from '@pluggable/web-app/utils';


import './App.css';


export default class App extends React.Component {
    static debugging = null;
    static propTypes = exact({});
    static _plugins = []
    static addPlugins (plugins) {
	App._plugins.push.apply(App._plugins, plugins);
    }

    state = {loaded: false}

    constructor(props) {
        super(props);
	console.log('setting debugging', App.debugging);
        this.app = new PluggableWebApp(App.debugging, this.onReady);
	this.app.log('configuring plugins')
        App._plugins.forEach(AppPlugin => {new PluginWrapper(AppPlugin, this.app).configure();});
	Object.values(this.app.plugins).forEach(p => p.addPluginHooks());
	this.app.log('plugins configured')
        this.state = {password: null, loggedIn: false, credentials: false};
    }

    onReady = () => {
	this.setState({ready: true})
    }

    onLogin = (result) => {
	this.setState(result);
    }

    async componentWillMount () {
	try {
	    await this.app.load();
	    this.setState({loaded: true});
	} catch (err) {
	    console.warn(err);
	}
    }

    render() {
	const {loaded, ready} = this.state;
	if (!loaded && !ready) {
	    return '';
	}
	const {app} = this;
	const {widgets} = app;
	let Layout = widgets['layout'];
        return (
	    <Layout loaded={loaded} />);
    }
}
