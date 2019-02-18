
import React from 'react';
import PropTypes from 'prop-types';
import exact from 'prop-types-exact';


export default class LoginNoAccount extends React.Component {
    static propTypes = exact({
	// app
	widgets: PropTypes.object.isRequired,

	// listening to auth.panels.close
	signal: PropTypes.object,
        compact: PropTypes.bool,
        targets: PropTypes.array,
        provided: PropTypes.object,
	fetched: PropTypes.func,
    })

    render () {
	const {signal, widgets} = this.props;
	const {
	    button: Button,
            h3: H3,
            'auth.signup.oauth': OAuth,
	    jumbotron: Jumbotron} = widgets;
	
	if (signal) {
	    return '';
	}	
	return (
            <Jumbotron>
              <div className="lead">
                <H3>{'msgNoAccount'}</H3>
                <Button>
                  {'buttonLabelSignupHere'}
                </Button>
	      </div>
              <div className="lead">              
	        <OAuth />
              </div>
            </Jumbotron>);
    }
}
