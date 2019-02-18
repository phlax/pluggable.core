
import React from 'react';
import ReactDOM from 'react-dom';

import App from '@pluggable/core/ui/App';
import '@pluggable/core/ui/app.plugged.js'
import '@pluggable/core/index.css';
import * as serviceWorker from '@pluggable/core/serviceworker';


ReactDOM.render(
    <App />,
    document.getElementById('root'));


// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
