

export default class RegisterAction {

    constructor (app) {
	this.app = app;
    }
    
    act = (context) => {
	const {signals} = this.app;
	signals.emit('auth.signup.success', {});	
	return {errors: [], response: {}};
    }    
}
