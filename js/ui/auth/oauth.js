
import React from 'react';


export default class OAuthProviders extends React.PureComponent {

    render () {
	const {oauth, signal, widgets} = this.props;
	if (signal) {
	    return '';
	}
	const {
            'h4': H4,
	    'auth.signup.oauth.provider': OAuthProvider} = widgets;
	return (
	    <div>
              <hr />
	      <H4>{'titleLoginWithOAuth'}</H4>
	      <div className="text-center">
	        {Object.keys(oauth).map((k, i) => {
                    return (
                        <span key={i}>
                          <OAuthProvider
                            provider={oauth[k]}  />{' '}
                        </span>
                    );
                })}
	      </div>
	    </div>            
	);
    }
}
