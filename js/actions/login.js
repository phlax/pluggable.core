

export default class LoginAction {

    constructor (app) {
	this.app = app;
    }

    act = async (context) => {
	const {username, password} = context;
	const {session, signals} = this.app;
        const {'auth.authenticate': authenticate} = session;
	const auth = await authenticate(
            username,
            password);
	signals.emit('auth.panels.close');	
	signals.emit('auth.login.success', auth);	
	return [];
    }
}
