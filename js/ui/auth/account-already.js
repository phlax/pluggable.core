
import React from 'react';
import PropTypes from 'prop-types';
import exact from 'prop-types-exact';


export default class SignupAccountAlready extends React.Component {
    static propTypes = exact({
	// app
	l10n: PropTypes.object.isRequired,
	widgets: PropTypes.object.isRequired,

	// listening to auth.panels.close
	signal: PropTypes.object,
        compact: PropTypes.bool,
        targets: PropTypes.array,
        provided: PropTypes.object

    })

    render () {
	const {signal, widgets} = this.props;
	const {
	    button: Button,
	    h3: H3,
	    jumbotron: Jumbotron} = widgets;

	if (signal) {
	    return '';
	}
	
	return (
            <Jumbotron>
              <H3>{'msgAccountAlready'}</H3>
              <p className="lead">		
                <Button color="secondary">
                  {'buttonLabelLoginHere'}
                </Button>
              </p>
            </Jumbotron>);
    }
}
