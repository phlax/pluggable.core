
import React from 'react';
import PropTypes from 'prop-types';
import exact from 'prop-types-exact';


export default class Applications extends React.PureComponent {
    static propTypes = exact({
	// app
	active: PropTypes.object.isRequired,
	apps: PropTypes.object.isRequired,
	signals: PropTypes.object.isRequired,
	widgets: PropTypes.object.isRequired,

	id: PropTypes.string.isRequired});

    onClick = (evt) => {
	const {name} = evt.currentTarget;
	const {apps, id, signals} = this.props;
	signals.emit('ui.app.switch', apps[name]);
	signals.emit('ui.window.close', id);
    }

    render () {
        const {active, apps, widgets} = this.props;
	const {user} = active;
        const {'card.deck': CardDeck} = widgets;
        const cards = Object.keys(apps)
	      .filter(k => {
		  if (apps[k].permission && !user) {
		      return false
		  }
		  return true;
	      })
	      .map((k, i) => {
		  let v = apps[k];
		  return {
		      className: 'centered',
		      name: k,
                      image: {src: v.icon, alt: v.title},
                      title: {text: v.title, truncate: 23},
                      button: {
			  color: 'primary',
			  size: 'lg',
			  onClick: this.onClick,
			  label: "buttonGoLabel"}};
              });
	return (
	    <CardDeck cards={cards} />
        );
    }
}
