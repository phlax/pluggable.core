
import React from 'react';


export default class SignupSucess extends React.PureComponent {

    onClick = () => {
        const {signals} = this.props;
        signals.emit('auth.register.complete');
    }
    
    render () {
	const {l10n, widgets} = this.props;
	const {
	    button: Button,
	    jumbotron: Jumbotron} = widgets;	
	return (
            <Jumbotron>
              <p className="lead">
	        {l10n['responseRegisterSuccess']}
              </p>
              <p className="lead">              
                <Button onClick={this.onClick}>
                  {'buttonLabelContinue'}
                </Button>
              </p>
            </Jumbotron>);
    }
}
