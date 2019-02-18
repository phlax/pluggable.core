
import React from 'react';


export default class LoginSucess extends React.PureComponent {

    render () {
	const {l10n, widgets} = this.props;
	const {jumbotron: Jumbotron} = widgets;	
	return (
            <Jumbotron>
              {l10n['responseLoginSuccess']}
            </Jumbotron>);
    }
}
