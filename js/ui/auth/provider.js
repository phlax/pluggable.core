
import React from 'react';


export default class OAuthProvider extends React.PureComponent {

    onClick = async (evt) => {
	// move this to a signal, or the whole lot to a button
        const {server} = this.props;
        const redirect = await server.call({
	    cmd: 'auth.social.request',
	    params: {provider: 'foo'}});
        window.location = redirect;	
    }
    
    render () {
        const {provider, widgets} = this.props;
	const {
	    media: Media,
	    button: Button} = widgets;
        return (
	    <Button
	      color="link"
              name={provider.name}
              onClick={this.onClick}>
              <Media
                object
                className="icon-xl"
                src={provider.icon} />
	    </Button>
	);
    }
}
